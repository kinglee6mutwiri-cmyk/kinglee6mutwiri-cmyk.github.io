#!/usr/bin/env python3

import os
import re
from pathlib import Path

ROOT = Path(".").resolve()

SKIP_DIRS = {
    ".git",
    ".github",
    "node_modules",
    ".venv",
    "venv"
}

HTML_FILES = [
    p for p in ROOT.rglob("*.html")
    if not any(part in SKIP_DIRS for part in p.parts)
]

fixed = 0
warnings = 0
errors = 0

print("=" * 60)
print("        WEBSITE AUTO FIX + ERROR SCANNER")
print("=" * 60)
print(f"HTML pages found: {len(HTML_FILES)}")
print()

def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")

def write_file(path, content):
    path.write_text(content, encoding="utf-8")

def check_html(path):
    global fixed, warnings, errors

    original = read_file(path)
    content = original

    # ---------------------------------------------------------
    # 1. Add missing <title>
    # ---------------------------------------------------------
    if not re.search(r"<title\b[^>]*>.*?</title>", content, re.I | re.S):
        filename = path.stem.replace("-", " ").replace("_", " ").title()

        if re.search(r"<head\b[^>]*>", content, re.I):
            content = re.sub(
                r"(<head\b[^>]*>)",
                r"\1\n    <title>" + filename + "</title>",
                content,
                count=1,
                flags=re.I
            )
            print(f"  AUTO-FIX: Added <title> to {path}")
            fixed += 1
        else:
            print(f"  ERROR: Missing <head> in {path}")
            errors += 1

    # ---------------------------------------------------------
    # 2. Add missing meta viewport
    # ---------------------------------------------------------
    if not re.search(
        r'<meta\s+[^>]*name=["\']viewport["\']',
        content,
        re.I
    ):
        viewport = (
            '<meta name="viewport" '
            'content="width=device-width, initial-scale=1.0">'
        )

        if re.search(r"<head\b[^>]*>", content, re.I):
            content = re.sub(
                r"(<head\b[^>]*>)",
                r"\1\n    " + viewport,
                content,
                count=1,
                flags=re.I
            )
            print(f"  AUTO-FIX: Added viewport to {path}")
            fixed += 1

    # ---------------------------------------------------------
    # 3. Add missing alt="" to images
    # ---------------------------------------------------------
    def fix_img(match):
        nonlocal content
        tag = match.group(0)

        if re.search(r"\balt\s*=", tag, re.I):
            return tag

        return tag[:-1] + ' alt="">'

    new_content = re.sub(
        r"<img\b[^>]*>",
        fix_img,
        content,
        flags=re.I
    )

    if new_content != content:
        print(f"  AUTO-FIX: Added missing alt attributes in {path}")
        fixed += 1
        content = new_content

    # ---------------------------------------------------------
    # 4. Detect empty links
    # ---------------------------------------------------------
    for match in re.finditer(
        r'<a\b[^>]*href\s*=\s*["\']\s*["\'][^>]*>',
        content,
        re.I
    ):
        print(
            f"  WARNING: Empty link found in {path} "
            f"(around character {match.start()})"
        )
        warnings += 1

    # ---------------------------------------------------------
    # 5. Detect missing href links
    # ---------------------------------------------------------
    for match in re.finditer(r"<a\b[^>]*>", content, re.I):
        tag = match.group(0)

        if not re.search(r"\bhref\s*=", tag, re.I):
            print(
                f"  WARNING: <a> without href in {path} "
                f"(around character {match.start()})"
            )
            warnings += 1

    # ---------------------------------------------------------
    # 6. Detect local image/file references
    # ---------------------------------------------------------
    for match in re.finditer(
        r'<(?:img|script|link)\b[^>]*(?:src|href)\s*=\s*["\']([^"\']+)["\']',
        content,
        re.I
    ):
        reference = match.group(1).strip()

        if (
            not reference
            or reference.startswith("#")
            or reference.startswith("http://")
            or reference.startswith("https://")
            or reference.startswith("//")
            or reference.startswith("data:")
            or reference.startswith("mailto:")
            or reference.startswith("tel:")
        ):
            continue

        reference = reference.split("#")[0].split("?")[0]

        if reference.startswith("/"):
            target = ROOT / reference.lstrip("/")
        else:
            target = path.parent / reference

        if not target.exists():
            print(
                f"  ERROR: Missing referenced file: "
                f"{reference} in {path}"
            )
            errors += 1

    # ---------------------------------------------------------
    # 7. Check important HTML structure
    # ---------------------------------------------------------
    if not re.search(r"<html\b", content, re.I):
        print(f"  ERROR: Missing <html> tag in {path}")
        errors += 1

    if not re.search(r"<head\b", content, re.I):
        print(f"  ERROR: Missing <head> tag in {path}")
        errors += 1

    if not re.search(r"<body\b", content, re.I):
        print(f"  ERROR: Missing <body> tag in {path}")
        errors += 1

    # ---------------------------------------------------------
    # 8. Check unclosed basic tags
    # ---------------------------------------------------------
    basic_tags = ["html", "head", "body", "title"]

    for tag in basic_tags:
        opening = len(re.findall(rf"<{tag}\b", content, re.I))
        closing = len(re.findall(rf"</{tag}>", content, re.I))

        if opening != closing:
            print(
                f"  ERROR: Possible unclosed <{tag}> tag in {path}"
            )
            errors += 1

    # ---------------------------------------------------------
    # Save only if changes were made
    # ---------------------------------------------------------
    if content != original:
        write_file(path, content)

    return


for html_file in HTML_FILES:
    print(f"Checking: {html_file}")
    check_html(html_file)
    print()

# -------------------------------------------------------------
# Check common required site files
# -------------------------------------------------------------
print("-" * 60)
print("CHECKING SITE FILES")
print("-" * 60)

required_files = [
    "index.html",
    "404.html",
    "robots.txt",
    "sitemap.xml"
]

for filename in required_files:
    file_path = ROOT / filename

    if file_path.exists():
        print(f"  ✓ {filename}")
    else:
        print(f"  WARNING: Missing {filename}")
        warnings += 1

# -------------------------------------------------------------
# Check CNAME
# -------------------------------------------------------------
cname = ROOT / "CNAME"

if cname.exists():
    domain = read_file(cname).strip()

    if domain:
        print(f"  ✓ CNAME: {domain}")
    else:
        print("  WARNING: CNAME exists but is empty")
        warnings += 1
else:
    print("  INFO: No CNAME file found")

# -------------------------------------------------------------
# Final report
# -------------------------------------------------------------
print()
print("=" * 60)
print("                    FINAL REPORT")
print("=" * 60)

print(f"Pages scanned : {len(HTML_FILES)}")
print(f"Auto-fixes    : {fixed}")
print(f"Warnings      : {warnings}")
print(f"Errors        : {errors}")

print("=" * 60)

if errors > 0:
    print("RESULT: FAILED")
    print("Fix the errors above before pushing to GitHub.")
    exit(1)

elif warnings > 0:
    print("RESULT: PASSED WITH WARNINGS")
    print("The site can be pushed, but review the warnings.")

else:
    print("RESULT: ALL CLEAR")
    print("No errors or warnings detected.")

exit(0)

