import re

ORIGINAL_FILE = "script.rpy"
TRANSLATION_FILE = "extracted_translated_cleaned.txt"
OUTPUT_FILE = "script_translated_original_positions.rpy"

# Pattern: 29 "Translated text"
translation_pattern = re.compile(r'^(\d+)\s+"(.*)"\s*$')

# Pattern for comment dialog:
comment_dialog_pattern = re.compile(
    r'(?P<prefix>\s*#\s*[^"“]*)(?P<open>["“])(?P<text>.*?)(?P<close>["”])'
)

# Pattern marking reference IDs in script:
reference_pattern = re.compile(r'#\s*game/script\.rpy:(\d+)')

# Detect translation blocks
translate_strings_start = re.compile(r'^\s*translate\s+chinese\s+strings\s*:')
old_pattern = re.compile(r'^\s*old\s+"(.*?)"')
new_pattern = re.compile(r'^\s*new\s*""\s*$')


def load_translations():
    translations = {}
    with open(TRANSLATION_FILE, "r", encoding="utf-8") as f:
        for line in f:
            m = translation_pattern.match(line.strip())
            if m:
                num, text = m.groups()
                translations[num] = text
    return translations


def main():
    translations = load_translations()
    current_ref = None
    inside_strings_block = False
    already_inserted = set()  # Prevent duplicate insertion per ref
    output = []

    with open(ORIGINAL_FILE, "r", encoding="utf-8") as f:
        for line in f:

            stripped = line.strip()

            # --- Detect entering translate chinese strings block ---
            if translate_strings_start.match(line):
                inside_strings_block = True
                output.append(line)
                continue

            # --- Handle lines inside translate chinese strings block ---
            if inside_strings_block:
                if stripped == "":
                    output.append(line)
                    continue
                if not line.startswith(" "):
                    inside_strings_block = False
                    current_ref = None
                    output.append(line)
                    continue

                # Detect reference ID
                ref_match = reference_pattern.search(line)
                if ref_match:
                    current_ref = ref_match.group(1)
                    output.append(line)
                    continue

                # Replace old line with Chinese text, leave new empty
                old_match = old_pattern.match(line)
                if old_match and current_ref in translations:
                    translated_text = translations[current_ref]
                    indent = line[:line.index("old")]
                    new_line = f'{indent}old "{translated_text}"\n'
                    output.append(new_line)
                    already_inserted.add(current_ref)
                    continue

                # Leave other lines untouched
                output.append(line)
                continue

            # --- Outside translate chinese strings block ---
            # Detect reference IDs for normal blocks
            ref_match = reference_pattern.search(line)
            if ref_match:
                current_ref = ref_match.group(1)

            # Translate comment dialog (# or # e)
            dialog_match = comment_dialog_pattern.search(line)
            if dialog_match and current_ref in translations:
                translated = translations[current_ref]
                prefix = dialog_match.group("prefix")
                open_q = dialog_match.group("open")
                close_q = dialog_match.group("close")
                new_line = f"{prefix}{open_q}{translated}{close_q}\n"
                output.append(new_line)
                already_inserted.add(current_ref)
                continue

            # Otherwise, leave line untouched
            output.append(line)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.writelines(output)

    print(f"✓ Translations inserted into all blocks → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
