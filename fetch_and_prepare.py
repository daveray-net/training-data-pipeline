import yfinance as yf
import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from datasets import Dataset
import json
import os
import time
import schedule
import logging
import tabulate

# ────────────────────────────────────────────────
# CONFIG – edit values here as needed
# ────────────────────────────────────────────────

CONFIG = {
    # Data fetching
    'NQ_TICKER':                "MNQ=F",
    'DAYS_BACK':                7,                     # how far back to fetch on first run or empty DB
    'MIN_FRESH_AGE_MINUTES':    1440,                  # default=10... skip fetch if latest data is newer than this
    'FETCH_OVERLAP_MINUTES':    5,                     # small buffer when fetching incrementally

    # Data preparation
    'MAX_ROWS_FOR_EXAMPLES':    8000,
    'WINDOW_SIZE':              20,                    # bars shown in each prompt example
    'FUTURE_BARS':              5,                     # how many bars ahead for labeling return

    # Scheduling & paths
    'SCHEDULE_TIME':            "04:30",               # daily run time (24h format)
    'DATA_DIR':                 "/app/data",
    'DB_PREFIX':                "sqlite:///",
    'DB_FILENAME':              "nq_data_yf.db",
    'JSONL_FILENAME':           "trading_examples.jsonl",
}

# Derived paths (computed once)
DB_PATH = os.path.join(CONFIG['DATA_DIR'], CONFIG['DB_FILENAME'])
JSONL_PATH = os.path.join(CONFIG['DATA_DIR'], CONFIG['JSONL_FILENAME'])

# ────────────────────────────────────────────────
# Configure logging once at module level
# ────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler()  # to console
        # logging.FileHandler('/app/data/fetch.log')  # uncomment to also log to file
    ]
)

logger = logging.getLogger(__name__)

logger.info(f"DB_PATH={DB_PATH}");
logger.info(f"DB_PREFIX={CONFIG['DB_PREFIX']}");
logger.info(f"JSONL_PATH={JSONL_PATH}");

# Example for a local SQLite database
DATABASE_URL = CONFIG['DB_PREFIX']+DB_PATH;
logger.info(f"DATABASE_URL={DATABASE_URL}");

# This line defines the 'engine' variable that was missing
engine = create_engine(DATABASE_URL)

# ────────────────────────────────────────────────
# Fetch functions
# ────────────────────────────────────────────────
def get_latest_timestamp():
    """Retrieve the most recent timestamp from the database (or None if empty/error)."""
    try:
        query = "SELECT MAX(timestamp) as last_ts FROM bars_1m"
        result = pd.read_sql(query, engine)
        last_ts_str = result['last_ts'].iloc[0]

        if pd.isna(last_ts_str):
            logger.debug("No timestamps found in database (empty table)")
            return None

        last_ts = pd.to_datetime(last_ts_str)
        logger.debug(f"Latest timestamp in DB: {last_ts}")
        return last_ts

    except Exception as e:
        logger.error(f"Failed to read latest timestamp from DB: {e}")
        return None


def should_fetch_new_data():
    min_fresh_age_minutes = CONFIG['MIN_FRESH_AGE_MINUTES']

    now = datetime.now()
    logger.debug(f"Checking freshness at {now}")

    last_ts = get_latest_timestamp()

    if last_ts is None:
        logger.info("Database is empty → will fetch full recent period")
        return True, None, now

    age_minutes = (now - last_ts).total_seconds() / 60
    if age_minutes < min_fresh_age_minutes:
        logger.info(f"Data is fresh ({age_minutes:.1f} min old) → skipping fetch")
        return False, last_ts, now
    else:
        logger.info(f"Data is stale ({age_minutes:.1f} min old) → will fetch updates")
        return True, last_ts, now


def fetch_recent_1m():
    days_back = CONFIG['DAYS_BACK']
    min_fresh_age_minutes = CONFIG['MIN_FRESH_AGE_MINUTES']
    overlap_minutes = CONFIG['FETCH_OVERLAP_MINUTES']

    should_fetch, last_ts, now = should_fetch_new_data()

    if not should_fetch:
        logger.debug("Fetch skipped – returning empty DataFrame")
        return pd.DataFrame()

    # Determine time window
    if last_ts is None:
        start = now - timedelta(days=days_back + 1)
        logger.info(f"First fetch → requesting {days_back}+ days back from {start.date()}")
    else:
        start = last_ts - timedelta(minutes=overlap_minutes)
        logger.info(f"Incremental fetch → starting from {start} (with {overlap_minutes}-min buffer)")

    end = now
    logger.debug(f"Fetching range: {start} → {end}")

    # Download
    try:
        df = yf.download(
            CONFIG['NQ_TICKER'],
            start=start,
            end=end,
            interval="1m",
            prepost=False,
            progress=False
        )
    except Exception as e:
        logger.error(f"yfinance download failed: {e}")
        return pd.DataFrame()

    if df.empty:
        logger.warning("yfinance returned empty DataFrame")
        return pd.DataFrame()

    logger.info(f"yfinance returned {len(df)} raw bars")

    # Clean & standardize
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
    df.index.name = 'timestamp'
    df.reset_index(inplace=True)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

    # Filter new rows only
    if last_ts is not None:
        old_len = len(df)
        df = df[df['timestamp'] > last_ts]
        filtered_count = old_len - len(df)
        if filtered_count > 0:
            logger.debug(f"Filtered out {filtered_count} old bars")

    if df.empty:
        logger.info("No new bars after timestamp filtering")
        return pd.DataFrame()

    # Store
    try:
        df.to_sql('bars_1m', engine, if_exists='append', index=False)
        logger.info(f"Successfully appended {len(df)} new 1m bars at {now.strftime('%Y-%m-%d %H:%M:%S')}")
    except Exception as e:
        logger.error(f"Failed to write new bars to database: {e}")
        return pd.DataFrame()

    return df

# ────────────────────────────────────────────────
# Data preparation & labeling
# ────────────────────────────────────────────────

def prepare_examples():
    """Final Integrated Pipeline: Markdown Tables + NaN Cleanup + Step-by-Step Reasoning"""
    max_rows    = CONFIG['MAX_ROWS_FOR_EXAMPLES']
    window_size = CONFIG['WINDOW_SIZE']
    future_bars = CONFIG['FUTURE_BARS']

    try:
        # Step 1: Fetch with extra padding for indicators
        query = f"SELECT * FROM bars_1m ORDER BY timestamp DESC LIMIT {max_rows}"
        df = pd.read_sql(query, engine)
    except Exception as e:
        logger.error(f"Database read failed: {e}")
        return []

    # Step 2: Prep and Sort
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df.set_index('timestamp', inplace=True)
    df.sort_index(inplace=True)

    # Step 3: Indicators
    df['rsi'] = ta.rsi(df['close'], length=14)
    macd_df = ta.macd(df['close'])
    df['macd'] = macd_df['MACD_12_26_9']
    df['macd_h'] = macd_df['MACDh_12_26_9'] # Histogram for momentum check

    # Step 4: THE FIX - Drop warm-up rows (NaNs)
    df.dropna(subset=['rsi', 'macd'], inplace=True)

    # Step 5: Labels
    df['future_return'] = df['close'].shift(-future_bars) - df['close']
    def get_action(ret):
        if ret > 2.0: return 'Long'
        if ret < -2.0: return 'Short'
        return 'Hold'
    df['action'] = df['future_return'].apply(get_action)

 ##   examples = []
    # Step 6: Build Examples
 ##   for i in range(len(df) - window_size - future_bars):
 ##       window_df = df.iloc[i : i + window_size].copy()
 ##       window_df['time'] = window_df.index.strftime('%H:%M')

 ##   for i in range(len(df) - window_size - future_bars):
 ##       window_df = df.iloc[i : i + window_size].copy()

 ##       # --- THE FIX: Continuity Check ---
 ##       # Calculate actual minutes elapsed in this window
 ##       time_diff = (window_df.index[-1] - window_df.index[0]).total_seconds() / 60

 ##       # If the window spans more than (window_size - 1) minutes, there's a gap
 ##       if time_diff > (window_size - 1):
 ##           continue # Skip this window; it contains a gap
 ##       # ---------------------------------

 ##       window_df['time'] = window_df.index.strftime('%H:%M')
 ##       # ... (rest of your existing Markdown and reasoning logic)

 ##       # Markdown Table
 ##       table_data = window_df[['time', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'macd']]
 ##       markdown_table = table_data.to_markdown(index=False, tablefmt="pipe", floatfmt=".2f")

 ##       # Context for Reasoning
 ##       curr = window_df.iloc[-1]
 ##       prev = window_df.iloc[-2]
 ##       label_row = df.iloc[i + window_size]
 ##       action = label_row['action']


    # ... (Steps 1-5 remain the same)

    examples = []
    for i in range(len(df) - window_size - future_bars):
        # The full span we care about: Window + Future look-ahead
        full_span = df.iloc[i : i + window_size + future_bars]

        # --- THE FULL FIX: Past & Future Continuity Check ---
        # Total expected minutes: (window_size + future_bars - 1)
        expected_mins = window_size + future_bars - 1
        actual_mins = (full_span.index[-1] - full_span.index[0]).total_seconds() / 60

        if actual_mins > expected_mins:
            continue # Skip if there's a gap anywhere in the input or the label
        # ----------------------------------------------------

        # Step 6: Build Examples
        window_df = df.iloc[i : i + window_size].copy()
        window_df['time'] = window_df.index.strftime('%H:%M')

        # Markdown Table for the prompt
        table_data = window_df[['time', 'open', 'high', 'low', 'close', 'volume', 'rsi', 'macd']]
        markdown_table = table_data.to_markdown(index=False, tablefmt="pipe", floatfmt=".2f")

        # Context for Reasoning
        # curr is the last bar in the table (the "now" for the model)
        curr = window_df.iloc[-1]
        prev = window_df.iloc[-2]

        # Use the pre-calculated action attached to the current bar
        action = curr['action']


        # ... (Rest of your reasoning and prompt logic is perfect)

        # Step-by-Step Logic
        reasons = []
        if action == "Long":
            if curr['rsi'] < 35: reasons.append("RSI is in oversold territory")
            if curr['macd'] > prev['macd']: reasons.append("MACD histogram is expanding upward")
            reasons.append(f"Price support held at {curr['low']}")
        elif action == "Short":
            if curr['rsi'] > 65: reasons.append("RSI is in overbought territory")
            if curr['macd'] < prev['macd']: reasons.append("MACD histogram is declining")
            reasons.append(f"Price resistance met at {curr['high']}")
        else:
            reasons.append("Indicators are neutral and RSI is midrange")

        reason_str = ". ".join(reasons)

        prompt = (
            f"### Recent NQ 1-minute bars:\n\n"
            f"{markdown_table}\n\n"
            "Analyze momentum, RSI, and MACD. Recommend next action: Long, Short, or Hold.\n"
            "Include confidence (0-100), stop-loss ticks from entry, and target ticks.\n"
            "Reason step-by-step."
        )

        response = (
            f"Action: {action}\n"
            f"Confidence: 75\n"
            f"Stop-loss: 10 ticks\n"
            f"Target: 20 ticks\n"
            f"Reason: {reason_str}. The current RSI of {curr['rsi']:.1f} and MACD of {curr['macd']:.2f} support a {action} bias for the next {future_bars} minutes."
        )

        examples.append({
            "messages": [
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
        })

    logger.info(f"Generated {len(examples)} clean examples.")
    return examples

def save_examples_markdown(filename, examples):
    with open(filename, 'w', encoding='utf-8') as f:
        for example in examples:
            # Setting indent=2 makes the file human-readable with real line breaks
            # ensure_ascii=False prevents weird character encoding
            json_record = json.dumps(example, indent=2, ensure_ascii=False)
            f.write(json_record + "\n")

def save_examples_jsonl(examples):
    with open(JSONL_PATH, 'w') as f:
        for ex in examples:
            f.write(json.dumps(ex) + '\n')

# ────────────────────────────────────────────────
# Main update loop
# ────────────────────────────────────────────────

def update_and_export():
    fetch_recent_1m()
    examples = prepare_examples()
    if examples:
        try:
            save_examples_jsonl(examples)
            print(f"Successfully exported {len(examples)} examples → {JSONL_PATH}")
            filename = JSONL_PATH+".md";
            save_examples_markdown(filename, examples)
            print(f"Successfully exported {len(examples)} examples → {filename}")

        except Exception as e:
            print(f"Export failed: {e}")
    else:
        print("No examples to export.")


# Schedule daily update (adjust time as preferred)
#schedule.every().day.at(CONFIG['SCHEDULE_TIME']).do(update_and_export)

if __name__ == "__main__":
    print("NQ Data Pipeline started.")
    update_and_export()  # Run once immediately on container start
#    while True:
#        schedule.run_pending()
#        time.sleep(60)
