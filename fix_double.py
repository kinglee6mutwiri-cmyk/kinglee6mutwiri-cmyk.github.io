from pathlib import Path
html = Path("index.html").read_text(encoding="utf-8")
html = html.replace(
    "Every article on this site is researched and written by me to add real value, not to fill space.",
    ""
)
Path("index.html").write_text(html, encoding="utf-8")
print("Removed duplicate line")
