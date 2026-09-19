from pathlib import Path
html = Path("index.html").read_text(encoding="utf-8")
html = html.replace(
    "This is why this homepage now contains over 2500 words of useful, unique content that shows Google and AdSense that this site is a serious publication with a long term vision.",
    "Every article on this site is researched and written by me to add real value, not to fill space."
)
Path("index.html").write_text(html, encoding="utf-8")
print("Fixed one sentence")
