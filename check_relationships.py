from pathlib import Path
from html.parser import HTMLParser
import re

FILE = Path("relationships-human-behaviour.html")

class Checker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.text_parts = []
        self.links = []
        self.images = []
        self.h1 = []
        self.title = ""
        self.meta = []
        self.canonical = None
        self.adsense = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)

        if tag == "a":
            self.links.append(attrs.get("href", ""))

        if tag == "img":
            self.images.append(attrs)

        if tag == "meta":
            self.meta.append(attrs)

        if tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href")

        if tag == "ins" and "adsbygoogle" in (attrs.get("class") or ""):
            self.adsense += 1

    def handle_data(self, data):
        text = data.strip()
        if text:
            self.text_parts.append(text)

    def handle_endtag(self, tag):
        pass

html = FILE.read_text(encoding="utf-8")

parser = Checker()
parser.feed(html)

# Title
m = re.search(r"<title[^>]*>(.*?)</title>", html, re.I | re.S)
title = re.sub(r"\s+", " ", m.group(1)).strip() if m else ""

# H1
h1s = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.I | re.S)
h1_text = [
    re.sub(r"<[^>]+>", " ", x)
    for x in h1s
]

# Visible text
text = " ".join(parser.text_parts)
text = re.sub(r"\s+", " ", text).strip()

# Remove CSS/JS-like leftovers if any
words = re.findall(r"\b[\w’'-]+\b", text, re.UNICODE)

internal_links = [
    x for x in parser.links
    if x and (
        x.startswith("/")
        or x.startswith("https://kinglee6mutwiri.co.ke/")
        or x.startswith("http://kinglee6mutwiri.co.ke/")
    )
]

external_links = [
    x for x in parser.links
    if x.startswith("http")
    and "kinglee6mutwiri.co.ke" not in x
]

warnings = []
errors = []

# File
if not FILE.exists():
    errors.append("File does not exist.")

# Basic HTML
if "<!DOCTYPE HTML>" not in html[:200].upper():
    warnings.append("DOCTYPE is missing or not at the beginning.")

if not re.search(r'<html[^>]+lang=["\']en["\']', html, re.I):
    warnings.append("English lang attribute is missing.")

if not re.search(r'<meta[^>]+charset=', html, re.I):
    errors.append("Charset meta tag is missing.")

if not re.search(r'<meta[^>]+name=["\']viewport["\']', html, re.I):
    errors.append("Viewport meta tag is missing.")

# Title
if not title:
    errors.append("Title is missing.")
elif len(title) < 30:
    warnings.append(f"Title is short ({len(title)} characters).")
elif len(title) > 65:
    warnings.append(f"Title may be long ({len(title)} characters).")

# Description
desc_match = re.search(
    r'<meta[^>]+name=["\']description["\'][^>]+content=["\'](.*?)["\']',
    html, re.I | re.S
)

description = desc_match.group(1).strip() if desc_match else ""

if not description:
    errors.append("Meta description is missing.")
elif len(description) < 120:
    warnings.append(f"Meta description is short ({len(description)} characters).")
elif len(description) > 170:
    warnings.append(f"Meta description may be long ({len(description)} characters).")

# Author
if not re.search(r'<meta[^>]+name=["\']author["\']', html, re.I):
    warnings.append("Author meta tag is missing.")

# Robots
if not re.search(r'<meta[^>]+name=["\']robots["\']', html, re.I):
    warnings.append("Robots meta tag is missing.")

# H1
if len(h1s) == 0:
    errors.append("No H1 found.")
elif len(h1s) > 1:
    warnings.append(f"Multiple H1 headings found ({len(h1s)}).")

# Canonical
if not parser.canonical:
    errors.append("Canonical URL is missing.")
else:
    expected = "https://kinglee6mutwiri.co.ke/relationships-human-behaviour.html"
    if parser.canonical != expected:
        errors.append("Canonical URL does not match this page.")

# Images
for i, img in enumerate(parser.images, 1):
    if not img.get("alt"):
        warnings.append(f"Image {i} has no alt text.")

# AdSense
if parser.adsense == 0:
    warnings.append("No AdSense ad unit found.")
elif parser.adsense > 3:
    warnings.append(f"{parser.adsense} AdSense units found; review ad density.")

if "ca-pub-5799841502846177" not in html:
    warnings.append("Expected AdSense publisher ID was not found.")

# Forbidden old wording
if "America AI" in html:
    errors.append('Forbidden phrase "America AI" found in file.')

# Placeholder checks
placeholders = [
    "lorem ipsum",
    "your-image-here",
    "example.com",
    "coming soon",
    "placeholder"
]

for item in placeholders:
    if item.lower() in html.lower():
        warnings.append(f"Possible placeholder text found: {item}")

# Broken-looking hrefs
for href in parser.links:
    if href in ("", "#", "javascript:void(0)", "javascript:void(0);"):
        warnings.append(f"Suspicious link found: {href!r}")

# Print report
print("=" * 60)
print("KINGLEE6 RELATIONSHIPS PAGE CHECK")
print("=" * 60)

print(f"\nFILE: {FILE}")
print(f"TITLE: {title}")
print(f"TITLE LENGTH: {len(title)} characters")
print(f"META DESCRIPTION LENGTH: {len(description)} characters")
print(f"H1 COUNT: {len(h1s)}")
print(f"IMAGE COUNT: {len(parser.images)}")
print(f"INTERNAL LINKS: {len(internal_links)}")
print(f"EXTERNAL LINKS: {len(external_links)}")
print(f"ADSENSE UNITS: {parser.adsense}")
print(f"WORD COUNT: {len(words)}")

print("\nH1:")
for h in h1_text:
    print(" -", re.sub(r"\s+", " ", h).strip())

print("\nCANONICAL:")
print(" -", parser.canonical)

print("\nERRORS:")
if errors:
    for e in errors:
        print(" [ERROR]", e)
else:
    print(" None")

print("\nWARNINGS:")
if warnings:
    for w in warnings:
        print(" [WARNING]", w)
else:
    print(" None")

print("\n" + "=" * 60)

if errors:
    print("RESULT: NEEDS FIXES")
elif warnings:
    print("RESULT: PASSES WITH WARNINGS")
else:
    print("RESULT: ALL CHECKS PASSED")

print("=" * 60)
