# patch.py
import re
import sys

def patch_bruteforceai():
    with open("BruteForceAI.py", "r", encoding="utf-8") as f:
        content = f.read()

    # Insert the run_default_mode function after the last import
    default_func = '''
def run_default_mode():
    """Called when no command-line arguments are provided."""
    import sys
    import yaml
    from BruteForceCore import BruteForceAI

    try:
        with open("config.yaml", "r") as f:
            config = yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading config.yaml: {e}")
        print("Please ensure config.yaml exists and is valid.")
        sys.exit(1)

    # Build a simple args object
    class Args:
        pass
    args = Args()
    args.command = 'attack'
    args.urls = config.get('targets', [])
    args.usernames = config.get('usernames', [])
    args.passwords = config.get('passwords', [])
    args.threads = config.get('threads', 5)
    args.llm_provider = config.get('llm_provider', 'ollama')
    args.llm_model = config.get('llm_model', 'llama2')
    args.groq_api_key = config.get('groq_api_key', '')
    args.timeout = config.get('timeout', 10)
    args.verbose = config.get('verbose', False)
    # Add any other fields that BruteForceAI expects

    ai = BruteForceAI(args)
    ai.run()   # adjust method name if needed (check BruteForceCore.py)
'''

    # Find the last import statement and insert after it
    # We'll use a regex to find the end of imports (including from ... import ...)
    import_pattern = r'^((?:from|import)\s+.*?)$'
    lines = content.splitlines()
    last_import_idx = -1
    for i, line in enumerate(lines):
        if re.match(import_pattern, line.strip()):
            last_import_idx = i
    if last_import_idx == -1:
        print("No import statements found; cannot patch.")
        sys.exit(1)

    # Insert the default function after the last import
    lines.insert(last_import_idx + 1, default_func)

    # Now modify the main block: replace the existing if __name__ == "__main__": section
    # We'll search for that block and replace it with our own
    new_main = '''
if __name__ == "__main__":
    import sys
    if len(sys.argv) == 1:
        run_default_mode()
    else:
        # preserve original main behavior
        main()
'''
    # Remove the old main block (from "if __name__ ..." to the end) and replace
    # We'll find the line with "if __name__ == "__main__":" and replace from there
    main_pattern = r'^if __name__ == "__main__":.*$'
    new_lines = []
    skip = False
    for line in lines:
        if re.match(main_pattern, line.strip()):
            # Start replacing from this line
            new_lines.append(new_main)
            skip = True
        elif skip:
            # If we are skipping, we stop when we hit a blank line or end? Actually we just skip everything until we see a line that is not indented? But simpler: we stop skipping after we've appended the new block.
            # We'll just skip all subsequent lines (the entire old main block)
            continue
        else:
            new_lines.append(line)

    # Write the modified content
    with open("BruteForceAI.py", "w", encoding="utf-8") as f:
        f.write("\n".join(new_lines))

    print("Patch applied successfully.")

if __name__ == "__main__":
    patch_bruteforceai()
