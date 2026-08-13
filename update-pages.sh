#!/data/data/com.termux/files/usr/bin/bash

FILE="index.html"

START="<!-- AUTO-PAGES-START -->"
END="<!-- AUTO-PAGES-END -->"

PAGES=""

for file in *.html; do

    # Skip homepage
    [ "$file" = "index.html" ] && continue

    # Skip error page if you have one
    [ "$file" = "404.html" ] && continue

    # Convert filename to readable title
    title="${file%.html}"
    title="${title//-/ }"
    title="${title//_/ }"

    # Capitalize first letter of each word
    title=$(echo "$title" | sed -E 's/(^| )([a-z])/\1\U\2/g')

    PAGES="$PAGES
    <a href=\"$file\" style=\"display:block; padding:15px; background:#f5f5f5; color:#111; text-decoration:none; border-radius:8px;\">
        $title
    </a>"
done

python - <<PY
from pathlib import Path

path = Path("$FILE")
html = path.read_text()

start = html.find("$START")
end = html.find("$END")

if start == -1 or end == -1:
    print("ERROR: AUTO-PAGES markers were not found.")
    exit(1)

content = '''$START
<div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:12px;">
$PAGES
</div>
$END'''

html = html[:start] + content + html[end + len("$END"):]

path.write_text(html)

print("Homepage links updated successfully.")
PY

