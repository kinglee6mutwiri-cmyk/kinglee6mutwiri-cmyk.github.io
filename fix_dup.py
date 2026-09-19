import re
from pathlib import Path

html = Path("index.html").read_text(encoding="utf-8")

# Find all <a href="..."> tags
seen = set()
def keep_first(m):
    href = m.group(1).strip()
    # normalize: remove trailing slash and lower
    norm = href.lower().replace("https://kinglee6mutwiri.co.ke","").strip("/")
    if norm == "": norm = "home"
    if norm in seen:
        print(f"REMOVED DUPLICATE: {href}")
        return ""  # delete duplicate
    seen.add(norm)
    return m.group(0)

html = re.sub(r'<a[^>]*href="([^"]+)"[^>]*>.*?</a>', keep_first, html, flags=re.I|re.S)

Path("index.html").write_text(html, encoding="utf-8")
print(f"Done. Kept {len(seen)} unique links.")
