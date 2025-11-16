import re

INPUT_FILE = "de_script.rpy"
OUTPUT_FILE = "extracted_comments.txt"

# Pattern to detect the reference line
ref_pattern = re.compile(r'#\s*game/script\.rpy:\s*(\d+)')

# Pattern to extract quoted text inside comment lines
quoted_pattern = re.compile(r'"(.*?)"')

def main():
    current_ref = None
    results = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            # Check for a reference line
            ref_match = ref_pattern.search(line)
            if ref_match:
                current_ref = ref_match.group(1)
                continue

            # Process comment lines only
            if line.strip().startswith("#") and current_ref is not None:
                # Extract all quoted strings inside the comment line
                quotes = quoted_pattern.findall(line)
                for q in quotes:
                    results.append(f'{current_ref} "{q}"')

    # Write output
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(results))

    print(f"Done! Extracted {len(results)} comment strings to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
