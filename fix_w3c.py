from pathlib import Path
import re

html = Path("index.html").read_text(encoding="utf-8")

# Fix both ad-wrap errors
html = html.replace(
    '<div class="ad-wrap" aria-label="Advertisement">',
    '<div class="ad-wrap" role="complementary" aria-label="Advertisement">'
)

# Also fix if you have variations with single quotes
html = re.sub(
    r'<div class="ad-wrap"\s+aria-label=',
    '<div class="ad-wrap" role="complementary" aria-label=',
    html
)

Path("index.html").write_text(html, encoding="utf-8")
print("Fixed W3C aria-label errors")
