import json
import sys

def view_dataset(filename, num_examples=None):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # If num_examples is None, it prints everything.
                # If it's a number, it stops when it hits that number.
                if num_examples is not None and i >= num_examples:
                    break

                record = json.loads(line)
                msgs = record['messages']

                # Restoring the correct indexes [0] and [1]
                print('[')
                print('  { "role": "user", "content": "')
                print(msgs[0]['content']) # Fixed index
                print('\n  }, {')
                print('\n"role": "assistant", "content": "')

                ast_content = msgs[1]['content'].strip() # Fixed index
                for l in ast_content.split('\n'):
                    print(f"> {l.strip()}  ")

                print('\n  } ]')

                # Visual separator
                if num_examples is None or i < num_examples - 1:
                    print(f"\n{'='*80}\n")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        # This is where it was likely stopping before
        print(f"Error processing record {i}: {e}")

if __name__ == "__main__":
    # Check if a filename was provided, else use default
    fname = sys.argv[1] if len(sys.argv) > 1 else 'trading_examples.jsonl'

    # Logic flip: if no second arg is provided, count is None (all records)
    count = int(sys.argv[2]) if len(sys.argv) > 2 else None

    view_dataset(fname, count)
