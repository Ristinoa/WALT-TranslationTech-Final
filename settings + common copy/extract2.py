import re

INPUT_FILE = "de.script.rpy"
OUTPUT_FILE = "extracted_comments.txt"

# Patterns
ref_pattern = re.compile(r'#\s*game/script\.rpy:(\d+)')
quoted_pattern = re.compile(r'"(.*?)"')
old_pattern = re.compile(r'^\s*old\s+"(.*?)"')
translate_start = re.compile(r'^\s*translate\s+german\s+strings\s*:')

def main():
    inside_translate = False
    current_ref = None
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()

            # Detect translate-block start
            if translate_start.match(line):
                inside_translate = True
                continue

            # Process inside translation block
            if inside_translate:
                # Exit only when indentation disappears on a NON-BLANK line
                if stripped and not line.startswith(" "):
                    inside_translate = False
                    current_ref = None
                    continue

                # Find reference
                ref_match = ref_pattern.search(line)
                if ref_match:
                    current_ref = ref_match.group(1)
                    continue

                # Extract "old" strings
                old_match = old_pattern.match(line)
                if old_match and current_ref:
                    text = old_match.group(1)
                    results.append(f'{current_ref} "{text}"')
                continue

            # Outside translation block: normal comment extraction
            ref_match = ref_pattern.search(line)
            if ref_match:
                current_ref = ref_match.group(1)
                continue

            if stripped.startswith("#") and current_ref:
                quotes = quoted_pattern.findall(line)
                for q in quotes:
                    results.append(f'{current_ref} "{q}"')

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(results))

    print(f"Done! Extracted {len(results)} entries.")

if __name__ == "__main__":
    main()
