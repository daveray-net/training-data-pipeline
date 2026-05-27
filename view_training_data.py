import json
import sys

def view_dataset(filename, num_examples=None): # Default to None for "all"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                # Only break if num_examples is set and we've hit the limit
                if num_examples is not None and i >= num_examples:
                    break

                record = json.loads(line)
                msgs = record['messages']

                # Opening bracket and first message role
                print('[')
                print('  { "role": "user", "content": "')

                # User Content (The Table + Prompt)
                print(msgs[0]['content'])

                # Object separator
                print('\n  }, {')

                # Assistant Role
                print('\n"role": "assistant", "content": "')

                # Assistant Content: Keyword per line, Blockquote, with Soft Returns
                ast_content = msgs[1]['content'].strip()
                for l in ast_content.split('\n'):
                    # The "  " at the end is the crucial soft return for Markdown
                    print(f"> {l.strip()}  ")

                # Final Closing Brackets
                print('\n  } ]')

                # Visual separator between records
                if i < num_examples - 1:
                    print(f"\n{'='*80}\n")

    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fname = sys.argv[1] if len(sys.argv) > 1 else 'trading_examples.jsonl'
    count = int(sys.argv[2]) if len(sys.argv) > 2 else 1
    view_dataset(fname, count)
