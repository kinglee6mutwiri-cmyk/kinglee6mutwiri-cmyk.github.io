from bs4 import BeautifulSoup
import sys
import re

if len(sys.argv) < 2:
    print("Usage: python3 check_page.py filename.html")
    sys.exit(1)

file = sys.argv[1]

with open(file, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

errors = []
warnings = []

# WORD COUNT
article = soup.find("article")

if article:
    text = article.get_text(" ", strip=True)
else:
    text = soup.get_text(" ", strip=True)

words = re.findall(r"\b[\w'-]+\b", text)
word_count = len(words)

# ERRORS
if not html.lower().lstrip().startswith("<!doctype html>"):
    errors.append("DOCTYPE declaration is missing")

if not soup.find("html"):
    errors.append("HTML tag is missing")

if not soup.find("head"):
    errors.append("HEAD tag is missing")

if not soup.find("body"):
    errors.append("BODY tag is missing")

if not soup.find("title"):
    errors.append("TITLE tag is missing")

if not soup.find("h1"):
    errors.append("H1 tag is missing")

# Check that every SCRIPT is somewhere inside HEAD or BODY
for script in soup.find_all("script"):
    inside_head = script.find_parent("head") is not None
    inside_body = script.find_parent("body") is not None

    if not inside_head and not inside_body:
        errors.append("SCRIPT tag found outside HEAD/BODY")

# AdSense loader
if "pagead2.googlesyndication.com/pagead/js" not in html:
    errors.append("AdSense loader is missing")

# GA4
if "G-S8VF9QWKET" not in html:
    warnings.append("GA4 tag G-S8VF9QWKET not found")

# WARNINGS
if word_count < 3000:
    warnings.append(f"Article is under 3,000 words ({word_count})")

title = soup.find("title")

if title:
    title_length = len(title.get_text(strip=True))
    if title_length > 60:
        warnings.append(f"Title is long ({title_length} characters)")

meta = soup.find("meta", attrs={"name": "description"})

if not meta:
    warnings.append("Meta description is missing")
else:
    description = meta.get("content", "")
    if len(description) > 160:
        warnings.append(
            f"Meta description is long ({len(description)} characters)"
        )

if not soup.find("link", rel="canonical"):
    warnings.append("Canonical link is missing")

if not soup.find("meta", attrs={"name": "viewport"}):
    warnings.append("Viewport meta tag is missing")

if not soup.find("img"):
    warnings.append("No images found")

# RESULTS
print()
print(file.upper())
print()
print(f"WORD COUNT : {word_count}")
print(f"ERRORS     : {len(errors)}")
print(f"WARNINGS   : {len(warnings)}")
print()

if errors:
    print("ERROR DETAILS:")
    for error in errors:
        print(f" - {error}")
    print()

if warnings:
    print("WARNING DETAILS:")
    for warning in warnings:
        print(f" - {warning}")
    print()

if not errors and not warnings:
    print("100% CLEAN — NO ERRORS OR WARNINGS")

print()
