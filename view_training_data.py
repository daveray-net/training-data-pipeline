import json
import sys

def view_dataset(filename, start=1, stop=None):
    try:
        # Convert human 1-based start to 0-based index for the loop
        start_idx = start - 1

        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # Skip until we hit the human-requested start
                if i < start_idx:
                    continue

                # Stop if we pass the human-requested stop (Inclusive)
                if stop is not None and i >= stop:
                    break

                record = json.loads(line)
                msgs = record['messages']

                # Outputting...
                #print(f"### Record {i+1}") # Showing 1-based record number
                #print('[ ')
                print(f"[ {i+1} ]") #record number as psuedo json style array index
                #print(' ] ')
                print('  { "role": "user", "content": "')
                print(msgs[0]['content'])
                print('\n  }, {\n\n"role": "assistant", "content": "')

                ast_content = msgs[1]['content'].strip()
                for l in ast_content.split('\n'):
                    print(f"> {l.strip()}  ")

                print('\n  } ]')
                print(f"\n{'='*80}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else 'trading_examples.jsonl'

    start_val = 1
    stop_val = None

    if len(sys.argv) > 2:
        val = sys.argv[2]
        if ":" in val:
            parts = val.split(":")
            # If user types "1:5", start_val is 1, stop_val is 5
            start_val = int(parts[0]) if parts[0] else 1
            stop_val = int(parts[1]) if parts[1] else None
        else:
            stop_val = int(val)

    view_dataset(fname, start_val, stop_val)
