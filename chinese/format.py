import re

INPUT_FILE = "options_extracted_ZH.txt"
OUTPUT_FILE = "options_extracted_ZH.txt"

# Matches: line starting with a number, then space, then anything
line_pattern = re.compile(r'^(\d+)\s+(.*)$')

def clean_line_text(text):
    # Remove all types of quotes inside the text
    text = text.replace("“", "")
    text = text.replace("”", "")
    text = text.replace('"', "")
    text = text.replace("‘", "")
    text = text.replace("’", "")
    text = text.replace("'", "")

    return text.strip()

def main():
    cleaned = []

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            line = raw.strip()
            if not line:
                continue

            m = line_pattern.match(line)
            if not m:
                # leave untouched if parsing fails
                cleaned.append(line)
                continue

            num = m.group(1)
            text = m.group(2)

            cleaned_text = clean_line_text(text)

            # Insert straight ASCII quotes around cleaned text
            new_line = f'{num} "{cleaned_text}"'
            cleaned.append(new_line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(cleaned))

    print(f"Done! Cleaned translations written to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
