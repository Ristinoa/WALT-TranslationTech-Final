import re

# Input and output file paths
input_file = "common.rpy"   # replace with your file name
output_file = "common_extracted.txt"

# Regex pattern to match lines like: # file.rpy:885
line_number_pattern = re.compile(r"# .*:(\d+)")
# Regex pattern to match old strings: old "string"
old_string_pattern = re.compile(r'old "(.*)"')

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

extracted = []
current_line_number = None

for line in lines:
    line = line.strip()
    
    # Check if it's a line with a line number
    line_number_match = line_number_pattern.match(line)
    if line_number_match:
        current_line_number = line_number_match.group(1)
        continue
    
    # Check if it's an old string
    old_string_match = old_string_pattern.match(line)
    if old_string_match and current_line_number:
        string_value = old_string_match.group(1)
        extracted.append(f'{current_line_number} "{string_value}"')
        current_line_number = None  # reset for next block

# Write to output file
with open(output_file, "w", encoding="utf-8") as f:
    f.write("\n".join(extracted))

print(f"Extraction complete! {len(extracted)} strings written to {output_file}")
