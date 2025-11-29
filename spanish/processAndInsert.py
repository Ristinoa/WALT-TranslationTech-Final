#!/usr/bin/env python3
import re
import io
import sys
import os

# ! This file is configured to work only on SPANISH files

#########################################
# 1. REGEX DEFINITIONS
#########################################

# Translation lines:   29 "Translated text"
translation_line_re = re.compile(r'^(\d+)\s+"(.*)"\s*$')

# Old line in strings block:    old "TEXT"
old_line_re = re.compile(r'^(\s*old\s*")(?P<content>.*)(".*)$')

first_quote_re = re.compile(r'"')
commented_source_re = re.compile(r'^\s*#\s*(?:\w+\s+)?".*"$')

strings_block_start = re.compile(
    r'^\s*translate\s+spanish\s+strings\s*:\s*$',
    re.IGNORECASE
)

# Pattern for formatting translation input lines
# NOTE: allow zero or more spaces after the numeric id to catch lines like `134「...」`
line_pattern = re.compile(r'^(\d+)\s*(.*)$')


#########################################
# 2. REFERENCE PATTERN SWITCHER
#########################################

REFERENCE_PATTERNS = {
    "script.rpy": re.compile(r'#\s*game/script\.rpy:(\d+)\b'),
    "screens.rpy": re.compile(r'#\s*game/screens\.rpy:(\d+)\b'),
    "common.rpy": re.compile(r'#\s*renpy/common/\S+?\.rpy:(\d+)\b'),
}


#########################################
# 3. HELPERS (UPDATED)
#########################################

def clean_line_text(text):
    # Removes styled quotes as well as special language variants
    if text is None:
        return ""

    # Normalize Unicode full-width space to normal then strip
    text = text.replace('\u3000', ' ')

    # Characters to remove from anywhere in the string
    remove_anywhere = [
        '“', '”', '"', '‘', '’', "'",   # ASCII & smart quotes
        '「', '」',                     # Japanese corner quotes
        '『', '』',                     # Chinese corner quotes
        '﹁', '﹂', '﹃', '﹄'            # other corner variants
    ]
    for ch in remove_anywhere:
        text = text.replace(ch, "")

    # Trim whitespace (both normal and any leftover full-width)
    text = text.strip().strip('\u3000')

    # If text still starts/ends with lingering quote-like punctuation, remove it
    while text and text[0] in ('"', '“', '「', '『', "'", '‘', '﹁'):
        text = text[1:]
    while text and text[-1] in ('"', '”', '」', '』', "'", '’', '﹂'):
        text = text[:-1]

    # Final trim
    return text.strip()


def escape_for_rpy(s: str) -> str:
    """Escape text so it is valid inside Ren’Py quoted strings."""
    return s.replace("\\", "\\\\").replace('"', '\\"')


#########################################
# 4. FORMAT TRANSLATION INPUT (FIXED)
#########################################

def format_input(INPUT_FILE, OUTPUT_FILE):
    """
    Read translation file (possibly produced by MT/CAT) and produce a normalized
    version where every line is: <id> "<clean text>"
    This accepts lines with or without a space after the numeric id.
    """
    cleaned = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for raw in f:
            # keep original raw for fallback, but operate on stripped for parsing
            orig = raw.rstrip("\n")
            line = orig.strip()
            if not line:
                continue

            m = line_pattern.match(line)
            if not m:
                # fallback: if the line looks like just text, try to preserve
                cleaned.append(line)
                continue

            num, text = m.groups()

            # If text is empty, preserve as empty quoted string
            if text is None or text.strip() == "":
                cleaned.append(f'{num} ""')
                continue

            cleaned_text = clean_line_text(text)
            # Always wrap cleaned_text in ASCII quotes (even if it's empty after cleaning)
            cleaned.append(f'{num} "{cleaned_text}"')

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        out.write("\n".join(cleaned))

    print(f"[✓] Cleaned translations written to {OUTPUT_FILE}")


#########################################
# 5. LOAD TRANSLATIONS
#########################################

def load_translations(path):
    translations = {}

    with io.open(path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            # Normalize smart quotes
            line = line.replace("“", '"').replace("”", '"')

            m = translation_line_re.match(line)
            if not m:
                continue

            key, txt = m.groups()
            translations[key] = txt

    return translations


#########################################
# 6. MAIN PROCESSING (unchanged)
#########################################

def process(original_path, translations, output_path, reference_re):
    out_lines = []
    current_ref = None
    inside_strings_block = False

    with io.open(original_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    total = len(lines)

    while i < total:
        line = lines[i]
        stripped = line.strip()

        # Start of translate block
        if strings_block_start.match(line):
            inside_strings_block = True
            out_lines.append(line)
            i += 1
            continue

        ###############################
        # INSIDE TRANSLATE BLOCK
        ###############################
        if inside_strings_block:

            # Block ends on blank line or non-indented line
            if stripped == "" or not line.startswith(" "):
                inside_strings_block = False
                current_ref = None
                out_lines.append(line)
                i += 1
                continue

            # Reference line
            ref_m = reference_re.search(line)
            if ref_m:
                current_ref = ref_m.group(1)
                out_lines.append(line)
                i += 1
                continue

            # Old "..." → replace text
            old_m = old_line_re.match(line)
            if old_m and current_ref and current_ref in translations:
                prefix = old_m.group(1)
                suffix = old_m.group(3)
                ch = escape_for_rpy(translations[current_ref])
                out_lines.append(f"{prefix}{ch}{suffix}\n")
                i += 1
                continue

            # Otherwise keep line
            out_lines.append(line)
            i += 1
            continue

        ###############################
        # OUTSIDE TRANSLATE BLOCK
        ###############################

        # Reference comment (update current_ref)
        ref_m = reference_re.search(line)
        if ref_m:
            current_ref = ref_m.group(1)
            out_lines.append(line)
            i += 1
            continue

        # Commented English line, followed by empty translation line
        if commented_source_re.match(line):
            out_lines.append(line)

            if i + 1 < total:
                next_line = lines[i + 1]
                quotes = [m.start() for m in first_quote_re.finditer(next_line)]

                if current_ref and current_ref in translations and len(quotes) >= 2:
                    q1, q2 = quotes[0], quotes[-1]
                    inner = next_line[q1 + 1 : q2]

                    if inner.strip() == "":
                        ch = escape_for_rpy(translations[current_ref])
                        new_next = (
                            next_line[: q1 + 1] +
                            ch +
                            next_line[q2 :]
                        )
                        out_lines.append(new_next)
                        i += 2
                        continue

            i += 1
            continue

        # Direct empty string case
        quotes = [m.start() for m in first_quote_re.finditer(line)]
        if current_ref and len(quotes) >= 2 and current_ref in translations:
            q1, q2 = quotes[0], quotes[-1]
            inner = line[q1 + 1 : q2]

            if inner.strip() == "":
                ch = escape_for_rpy(translations[current_ref])
                out_lines.append(line[: q1 + 1] + ch + line[q2 :])
                i += 1
                continue

        # Default passthrough
        out_lines.append(line)
        i += 1

    # Write output
    with io.open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(out_lines)

    print(f"[✓] Output written to {output_path}")


#########################################
# 7. MAIN DRIVER (unchanged)
#########################################

if __name__ == "__main__":

    original_files = ["script.rpy", "common.rpy", "screens.rpy"]
    translation_files = ["script_translated.txt", "common_extracted.txt", "screens_extracted.txt"]
    processed_files = ["script_translated_ES.txt", "common_extracted_Es.txt", "screens_extracted_ES.txt"]
    outputs = ["script_translated_final_ES.rpy", "common_translated_final_ES.rpy", "screens_translated_final_ES.rpy"]

    for i in range(len(original_files)):
        ORIG = original_files[i]
        TRANS_IN = translation_files[i]
        TRANS_OUT = processed_files[i]
        OUTPUT = outputs[i]

        print(f"\n=== Processing {ORIG} ===")

        # Format translation text
        format_input(TRANS_IN, TRANS_OUT)
        translations = load_translations(TRANS_OUT)

        if not translations:
            print(f"[ERROR] No translations found in {TRANS_OUT}")
            sys.exit(1)

        # Pick correct reference regex
        if ORIG not in REFERENCE_PATTERNS:
            print(f"[ERROR] No reference regex defined for {ORIG}")
            sys.exit(1)

        reference_re = REFERENCE_PATTERNS[ORIG]

        process(ORIG, translations, OUTPUT, reference_re)
