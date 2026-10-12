from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
from urllib.parse import urlparse, unquote
import re
import json

ROOT = Path(".")
SKIP = {".git", "node_modules", ".venv", "venv"}
errors, warnings, passed = [], [], []
pages = sorted(
    p for p in ROOT.rglob("*.html")
    if not any(x in SKIP for x in p.parts)
)

def add(level, page, msg):
    (errors if level == "ERROR" else warnings).append(
        (str(page), msg)
    )

class Parser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.title = ""
        self.desc = []
        self.canonical = []
        self.h1 = 0
        self.imgs = []
        self.links = []
        self.ids = set()
        self.duplicate_ids = []
        self.words = []
        self.in_title = False
        self.in_script = False
        self.head = False
        self.body = False
        self.outside_scripts = 0
        self.stack = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.tags.append(tag)

        if tag == "head":
            self.head = True
        if tag == "body":
            self.body = True
        if tag == "title":
            self.in_title = True
        if tag == "script":
            if not self.head and not self.body:
                self.outside_scripts += 1
            self.in_script = True
        if tag == "h1":
            self.h1 += 1
        if tag == "img":
            self.imgs.append(a)
        if tag == "a":
            self.links.append(a.get("href", ""))
        if a.get("id"):
            if a["id"] in self.ids:
                self.duplicate_ids.append(a["id"])
            self.ids.add(a["id"])
        if tag == "meta":
            if a.get("name", "").lower() == "description":
                self.desc.append(a.get("content", "").strip())
        if tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical.append(a.get("href", "").strip())

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script":
            self.in_script = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data
        if not self.in_script:
            self.words.append(data)

if not pages:
    print("ERROR: No HTML files found in", ROOT.resolve())
    raise SystemExit(1)

file_index = {}
for f in ROOT.rglob("*"):
    if f.is_file() and not any(x in SKIP for x in f.parts):
        file_index[f.as_posix().lstrip("./")] = f

page_data = {}
total_words = 0

for page in pages:
    try:
        raw = page.read_text(encoding="utf-8")
    except Exception as e:
        add("ERROR", page, f"Cannot read file: {e}")
        continue

    p = Parser()
    try:
        p.feed(raw)
        p.close()
    except Exception as e:
        add("ERROR", page, f"HTML parser failure: {e}")

    text = re.sub(r"\s+", " ", " ".join(p.words)).strip()
    count = len(re.findall(r"\b[\w’'-]+\b", text))
    total_words += count
    page_data[page] = (raw, p, count)

    if not re.search(r"<!doctype\s+html", raw, re.I):
        add("WARNING", page, "Missing HTML5 DOCTYPE")
    for tag in ("html", "head", "body"):
        if not re.search(fr"<{tag}\b", raw, re.I):
            add("ERROR", page, f"Missing <{tag}> element")
    if not re.search(r"</html\s*>", raw, re.I):
        add("WARNING", page, "Missing closing </html>")
    if not re.search(r"</head\s*>", raw, re.I):
        add("WARNING", page, "Missing closing </head>")
    if not re.search(r"</body\s*>", raw, re.I):
        add("WARNING", page, "Missing closing </body>")

    title = p.title.strip()
    if not title:
        add("ERROR", page, "Missing or empty title")
    elif len(title) > 60:
        add("WARNING", page, f"Long title: {len(title)} characters")
    elif len(title) < 20:
        add("WARNING", page, f"Short title: {len(title)} characters")

    if not p.desc or not p.desc[0]:
        add("WARNING", page, "Missing meta description")
    elif len(p.desc[0]) > 160:
        add("WARNING", page, f"Long meta description: {len(p.desc[0])} characters")
    elif len(p.desc[0]) < 70:
        add("WARNING", page, f"Short meta description: {len(p.desc[0])} characters")

    if not any(
        re.search(r'<meta\b[^>]*name=["\']viewport["\']', line, re.I)
        for line in raw.splitlines()
    ):
        add("WARNING", page, "Missing viewport meta tag")

    if p.h1 == 0:
        add("WARNING", page, "Missing H1 heading")
    elif p.h1 > 1:
        add("WARNING", page, f"Multiple H1 headings: {p.h1}")

    if not p.canonical:
        add("WARNING", page, "Missing canonical URL")
    elif len(set(p.canonical)) > 1:
        add("ERROR", page, "Conflicting canonical URLs")

    if any(not i.get("alt", "").strip() for i in p.imgs):
        add("WARNING", page, "One or more images have missing/empty alt text")

    for ident in set(p.duplicate_ids):
        add("WARNING", page, f"Duplicate id: {ident}")

    if p.outside_scripts:
        add("WARNING", page, "Script tag may be outside HEAD/BODY")

    if re.search(r"\[cite\s*:", raw, re.I):
        add("ERROR", page, "Citation placeholder [cite: ...] remains")
    if re.search(r"\b(lorem ipsum|insert text here|replace this text)\b", raw, re.I):
        add("WARNING", page, "Possible placeholder text")

    short_exempt = {
        "contact.html", "privacy-policy.html", "privacy.html",
        "terms.html", "disclaimer.html", "404.html", "about.html"
    }
    if count < 300 and page.name not in short_exempt:
        add("WARNING", page, f"Short content: {count} words")

    if not re.search(r'<meta\b[^>]*charset\s*=', raw, re.I):
        add("WARNING", page, "Missing character encoding declaration")

    for link in p.links:
        if not link or link.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        u = urlparse(link)
        if u.scheme and u.scheme not in ("http", "https"):
            continue
        if u.netloc:
            continue
        path = unquote(u.path).split("?")[0]
        if not path:
            continue
        target = (page.parent / path).as_posix() if not path.startswith("/") else path.lstrip("/")
        target = str(Path(target))
        if not Path(target).exists():
            add("WARNING", page, f"Internal link target not found: {link}")

# Check duplicate titles and canonical URLs across pages
title_map, canonical_map = {}, {}
for page, (raw, p, count) in page_data.items():
    if p.title.strip():
        title_map.setdefault(p.title.strip().lower(), []).append(str(page))
    for c in p.canonical:
        if c:
            canonical_map.setdefault(c, []).append(str(page))

for title, files in title_map.items():
    if len(files) > 1:
        for f in files:
            add("WARNING", f, f"Duplicate page title shared by: {', '.join(files)}")

for url, files in canonical_map.items():
    if len(files) > 1:
        for f in files:
            add("WARNING", f, f"Canonical URL shared by multiple files: {url}")

print("\n" + "=" * 65)
print("KINGLEE MUTWIRI WEBSITE — FULL LOCAL HTML AUDIT")
print("=" * 65)
print("Website directory :", ROOT.resolve())
print("HTML pages scanned:", len(pages))
print("Total word count  :", total_words)
print("Errors            :", len(errors))
print("Warnings          :", len(warnings))

print("\n" + "=" * 65)
print("PAGE-BY-PAGE WORD COUNTS")
print("=" * 65)
for page, (raw, p, count) in page_data.items():
    print(f"{str(page):55} {count:>6} words")

print("\n" + "=" * 65)
print("ERRORS")
print("=" * 65)
if errors:
    for page, msg in errors:
        print(f"[ERROR] {page}: {msg}")
else:
    print("No errors detected by these checks.")

print("\n" + "=" * 65)
print("WARNINGS")
print("=" * 65)
if warnings:
    for page, msg in warnings:
        print(f"[WARNING] {page}: {msg}")
else:
    print("No warnings detected by these checks.")

print("\n" + "=" * 65)
print("AUDIT COMPLETE — NO WEBSITE FILES WERE MODIFIED")
print("=" * 65)
