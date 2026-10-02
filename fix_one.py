file = "mindset-and-life.html"
line_to_fix = 1040
idx = line_to_fix - 1

with open(file, "r", encoding="utf-8") as f:
    lines = f.readlines()

print("BEFORE:", repr(lines[idx]))

# Keep same indentation as your file
indent = lines[idx][:len(lines[idx]) - len(lines[idx].lstrip())]

# Clean fix - only this heading, no other lines touched
# This removes any unclosed <span> <a> <b> etc inside it
lines[idx] = f"{indent}<h3>Luck and Risk</h3>\n"

print("AFTER :", repr(lines[idx]))

with open(file, "w", encoding="utf-8") as f:
    f.writelines(lines)

print(f"Fixed only line {line_to_fix}")
