import json
import sys

def view_dataset(filename, start=0, stop=None):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # Skip records until we hit the 'start' index
                if i < start:
                    continue

                # Stop if we hit the 'stop' index (if one was provided)
                if stop is not None and i >= stop:
                    break

                record = json.loads(line)
                msgs = record['messages']

                print(f"### Record {i}") # Added a record number for easy reference
                print('[')
                print('  { "role": "user", "content": "')
                print(msgs[0]['content'])
                print('\n  }, {')
                print('\n"role": "assistant", "content": "')

                ast_content = msgs[1]['content'].strip()
                for l in ast_content.split('\n'):
                    print(f"> {l.strip()}  ")

                print('\n  } ]')
                print(f"\n{'='*80}\n")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error on record {i}: {e}")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else 'trading_examples.jsonl'

    start_val = 0
    stop_val = None

    if len(sys.argv) > 2:
        val = sys.argv[2]
        if ":" in val:
            # Handles 10:20
            parts = val.split(":")
            start_val = int(parts[0]) if parts[0] else 0
            stop_val = int(parts[1]) if parts[1] else None
        else:
            # Handles just 10 (shows first 10)
            stop_val = int(val)

    view_dataset(fname, start_val, stop_val)
