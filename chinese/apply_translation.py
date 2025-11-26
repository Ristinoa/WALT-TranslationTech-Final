#!/usr/bin/env python3
import re
import io
import sys


# Load translations keyed by numeric reference (e.g. 29 -> Chinese text)
translation_line_re = re.compile(r'^(\d+)\s+"(.*)"\s*$')

# ! Need to a switcher connected to specific document names to select a distinct pattern
# ! This may be better suited for the main method within the for loop?
# ! i.e., if the origin document is "script.rpy" we would use this one:
# reference_re = re.compile(r'#\s*game/script\.rpy:(\d+)\b')

# But if the origin file is "common.rpy" then we would need to use this one:
# Detect the "# game/script.rpy:NN" reference lines
reference_re = re.compile(r'#\s*renpy/common/\S+?\.rpy:(\d+)\b')

# ! Reference for screens.rpy
# ? reference_re = re.compile(r'#\s*game/screens\.rpy:(\d+)\b')

# ! Reference for overwriting options.rpy (This can be removed)
reference_re = re.compile(r'#\s*game/options\.rpy:(\d+)\b')

# Detect the translate chinese strings: block header
# !! Needs to be modified for different applications—note: "chinese" 
strings_block_start = re.compile(r'^\s*translate\s+chinese\s+strings\s*:\s*$', re.IGNORECASE)
# strings_block_start = re.compile(r'^\s*translate\s+japanese\s+strings\s*:\s*$', re.IGNORECASE)
# strings_block_start = re.compile(r'^\s*translate\s+german\s+strings\s*:\s*$', re.IGNORECASE)
# strings_block_start = re.compile(r'^\s*translate\s+spanish\s+strings\s*:\s*$', re.IGNORECASE)

# Detect an old "..." line (for strings block)
old_line_re = re.compile(r'^(\s*old\s*")(?P<content>.*?)(\".*)$')

# Generic: find first and last quote on a line (to replace only quoted content)
first_quote_re = re.compile(r'"')

# Commented source lines (e.g. '# "English..."' or '# e "English..."')
commented_source_re = re.compile(r'^\s*#\s*(?:\w+\s+)?".*"$')

# Matches: line starting with a number, then space, then anything
line_pattern = re.compile(r'^(\d+)\s+(.*)$')

# Helper method for the format function
def clean_line_text(text):
    # Remove all types of quotes inside the text
    text = text.replace("“", "")
    text = text.replace("”", "")
    text = text.replace('"', "")
    text = text.replace("‘", "")
    text = text.replace("’", "")
    text = text.replace("'", "")

    return text.strip()

# Function for properly formatting inputs to use "" and not smart quotes
# Necessary for anything MT or Trados created as CAT tools use 

def format_input(INPUT_FILE, OUTPUT_FILE):
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

# Helper to escape quotes/backslashes for safe insertion into "" in .rpy
def escape_for_rpy(s: str) -> str:
    # Escape backslash first, then double quote
    return s.replace('\\', '\\\\').replace('"', '\\"')

def load_translations(path):
    translations = {}
    with io.open(path, 'r', encoding='utf-8') as f:
        for lineno, raw in enumerate(f, start=1):
            line = raw.rstrip('\n')

            # Normalize smart quotes
            line = line.replace("“", '"').replace("”", '"')

            if not line.strip():
                continue

            m = translation_line_re.match(line)
            if not m:
                # print(f"Warning: line {lineno} did not match: {line}")
                continue

            key, txt = m.groups()
            translations[key] = txt
    return translations


def process(original_path, translations, output_path):
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

        # Detect entering translate chinese strings: block
        if strings_block_start.match(line):
            inside_strings_block = True
            out_lines.append(line)
            i += 1
            continue

        if inside_strings_block:
            # If we encounter a non-indented (no-leading-space) or blank line that is not part of the block,
            # assume block ended (this mirrors your original file style).
            if stripped == "" or not line.startswith(" "):
                inside_strings_block = False
                current_ref = None
                out_lines.append(line)
                i += 1
                continue

            # Keep reference lines as-is but update current_ref
            ref_m = reference_re.search(line)
            if ref_m:
                current_ref = ref_m.group(1)
                out_lines.append(line)
                i += 1
                continue

            # If this is an old "..." line, replace the content between quotes with the Chinese translation
            old_m = old_line_re.match(line)
            if old_m and current_ref and current_ref in translations:
                prefix = old_m.group(1)   # includes indentation and 'old "'
                suffix = old_m.group(3)   # includes closing quote and anything after
                ch = translations[current_ref]
                ch_escaped = escape_for_rpy(ch)
                new_line = f'{prefix}{ch_escaped}{suffix}\n'
                out_lines.append(new_line)
                i += 1
                continue

            # otherwise pass through unchanged
            out_lines.append(line)
            i += 1
            continue

        # OUTSIDE strings block:

        # If this line contains a reference comment, update current_ref
        ref_m = reference_re.search(line)
        if ref_m:
            current_ref = ref_m.group(1)
            out_lines.append(line)
            i += 1
            continue

        # If this is a commented source line (e.g. '# "English..."' or '# e "English..."'), keep it,
        # then if the next non-empty line is a quoted empty string or a speaker "" or new "" line, fill it.
        if commented_source_re.match(line):
            out_lines.append(line)
            # look ahead to next line (if any)
            if i + 1 < total:
                next_line = lines[i + 1]
                next_stripped = next_line.strip()
                # Only act if there's a current_ref and a translation exists
                if current_ref and current_ref in translations:
                    # Find the first quote and last quote positions in next_line
                    # We will only replace if content between quotes is empty (or whitespace)
                    quotes = [m.start() for m in first_quote_re.finditer(next_line)]
                    if len(quotes) >= 2:
                        q1 = quotes[0]
                        q2 = quotes[-1]
                        inner = next_line[q1+1:q2]
                        # Only replace if inner is empty (or only whitespace)
                        if inner.strip() == "":
                            # Build new line without changing indentation or anything else except inner text
                            prefix = next_line[:q1+1]   # up to and including first quote
                            suffix = next_line[q2:]     # closing quote and rest (including newline)
                            ch = translations[current_ref]
                            ch_escaped = escape_for_rpy(ch)
                            new_next = f'{prefix}{ch_escaped}{suffix}'
                            out_lines.append(new_next)
                            i += 2
                            continue
                # else: either no translation or not an empty-quoted next line; just proceed normally
            i += 1
            continue

        # For safety: if a line itself is a quoted line (not commented) and empty and preceded by a reference (but the comment was missing),
        # we can attempt to insert as well. This handles cases like directly "" after ref.
        # If current_ref exists and this line is an empty quoted string (or e "", d "", new "")
        quotes = [m.start() for m in first_quote_re.finditer(line)]
        if current_ref and len(quotes) >= 2:
            q1 = quotes[0]
            q2 = quotes[-1]
            inner = line[q1+1:q2]
            if inner.strip() == "" and current_ref in translations:
                prefix = line[:q1+1]
                suffix = line[q2:]
                ch = translations[current_ref]
                ch_escaped = escape_for_rpy(ch)
                new_line = f'{prefix}{ch_escaped}{suffix}'
                out_lines.append(new_line)
                i += 1
                continue

        # Default passthrough
        out_lines.append(line)
        i += 1

    # Write output
    with io.open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(out_lines)

    print(f'✓ Written output to: {output_path}')

if __name__ == '__main__':
    # This is a mess, we'll see if she even runs!

    # ! Original files are all .rpy files
    original_files = ["script.rpy","common.rpy","screens.rpy"]

    # ! Translation files are the ones we get from MT or from Trados — Translated & processed are grouped
    translation_files = ["script_translated.txt","common_extracted.txt","screens_extracted.txt"]
    processed_files = ["script_translated_ZH.txt","common_extracted_ZH.txt","screens_extracted_ZH.txt"]

    # ! Output file names for where results will be written to (don't want to destroy 'client files')
    outputs = ["script_translated_final.rpy","common_translated_final.rpy","screens_translated_final.rpy"]

    # The idea is to blast-process this whole thing
    # use original files to format translation, deterrmine source, then insert according to primary list index
    for i in range(len(original_files)):
        ORIGINAL_FILE = original_files[i]
        OUTPUT_FILE = outputs[i]
        format_input(translation_files[i],processed_files[i])
        TRANSLATION_FILE = processed_files[i]

        translations = load_translations(TRANSLATION_FILE)
        if not translations:
            print("Error: No translations loaded. Check the translation file path and format.", file=sys.stderr)
            sys.exit(1)
        process(ORIGINAL_FILE, translations, OUTPUT_FILE)
