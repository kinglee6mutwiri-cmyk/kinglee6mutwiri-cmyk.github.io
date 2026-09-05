#!/usr/bin/env python3

import os
import re
import sys
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote

ROOT = Path(".").resolve()

SKIP_DIRS = {
    ".git",
    ".githooks",
    "node_modules",
    ".venv",
    "venv",
}

SITE_DOMAIN = "kinglee6mutwiri.co.ke"

errors = 0
warnings = 0
auto_fixes = 0

html_files = [
    p for p in ROOT.rglob("*.html")
    if not any(part in SKIP_DIRS for part in p.parts)
]

print()
print("=" * 70)
print("             FULL WEBSITE QUALITY SCANNER")
print("=" * 70)
print()
print(f"HTML pages found: {len(html_files)}")
print()


def read_file(path):
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(
            encoding="utf-8",
            errors="ignore"
        )


def write_file(path, content):
    path.write_text(content, encoding="utf-8")


def add_error(message):
    global errors
    print(f"  ERROR: {message}")
    errors += 1


def add_warning(message):
    global warnings
    print(f"  WARNING: {message}")
    warnings += 1


class PageParser(HTMLParser):

    def __init__(self):
        super().__init__()

        self.title = ""
        self.description = ""
        self.lang = None
        self.canonical = None

        self.h1_count = 0
        self.ids = []

        self.images_without_alt = 0
        self.links_without_href = 0
        self.empty_links = 0

        self.references = []

        self.in_title = False
        self.title_parts = []

        self.in_description = False

        self.has_nav = False
        self.has_footer = False

        self.has_adsense = False

        self.open_tags = []

    def handle_starttag(self, tag, attrs):

        attrs_dict = dict(attrs)

        tag = tag.lower()

        if tag == "html":
            self.lang = attrs_dict.get("lang")

        if tag == "title":
            self.in_title = True
            self.title_parts = []

        if tag == "meta":

            name = attrs_dict.get("name", "")
            content = attrs_dict.get("content", "")

            if name.lower() == "description":
                self.description = content.strip()

        if tag == "link":

            rel = attrs_dict.get("rel", "").lower()

            if "canonical" in rel:
                self.canonical = attrs_dict.get("href")

        if tag == "h1":
            self.h1_count += 1

        if "id" in attrs_dict:
            self.ids.append(attrs_dict["id"])

        if tag == "img":

            src = attrs_dict.get("src")

            if src:
                self.references.append(
                    ("image", src)
                )

            if "alt" not in attrs_dict:
                self.images_without_alt += 1

        if tag == "script":

            src = attrs_dict.get("src")

            if src:
                self.references.append(
                    ("script", src)
                )

            if src and "googlesyndication.com" in src:
                self.has_adsense = True

        if tag == "link":

            href = attrs_dict.get("href")

            if href:
                self.references.append(
                    ("link", href)
                )

        if tag == "a":

            href = attrs_dict.get("href")

            if href is None:
                self.links_without_href += 1

            elif href.strip() == "":
                self.empty_links += 1

            else:
                self.references.append(
                    ("link", href)
                )

        if tag == "nav":
            self.has_nav = True

        if tag == "footer":
            self.has_footer = True

        if tag not in {
            "meta",
            "link",
            "img",
            "input",
            "br",
            "hr",
            "source",
            "area",
            "base",
            "embed",
            "param",
            "track",
            "wbr"
        }:
            self.open_tags.append(tag)

    def handle_endtag(self, tag):

        tag = tag.lower()

        if tag == "title":
            self.in_title = False
            self.title = "".join(
                self.title_parts
            ).strip()

        if tag in self.open_tags:
            try:
                index = len(self.open_tags) - 1 - self.open_tags[::-1].index(tag)
                self.open_tags.pop(index)
            except ValueError:
                pass

    def handle_data(self, data):

        if self.in_title:
            self.title_parts.append(data)


def is_external(reference):

    ref = reference.strip()

    return (
        ref.startswith("http://")
        or ref.startswith("https://")
        or ref.startswith("//")
        or ref.startswith("mailto:")
        or ref.startswith("tel:")
        or ref.startswith("javascript:")
        or ref.startswith("data:")
    )


def clean_reference(reference):

    reference = unquote(reference)

    reference = reference.split("#")[0]
    reference = reference.split("?")[0]

    return reference


def resolve_local_file(page, reference):

    reference = clean_reference(reference)

    if not reference:
        return None

    if reference.startswith("/"):
        target = ROOT / reference.lstrip("/")
    else:
        target = page.parent / reference

    return target.resolve()


def auto_fix_page(path):

    global auto_fixes

    original = read_file(path)
    content = original

    # ---------------------------------------------------------
    # SAFE FIX 1: Missing viewport
    # ---------------------------------------------------------

    if not re.search(
        r'<meta\s+[^>]*name=["\']viewport["\']',
        content,
        re.I
    ):

        if re.search(
            r"<head\b[^>]*>",
            content,
            re.I
        ):

            content = re.sub(
                r"(<head\b[^>]*>)",
                r'\1\n    <meta name="viewport" content="width=device-width, initial-scale=1.0">',
                content,
                count=1,
                flags=re.I
            )

            print("  AUTO-FIX: Added mobile viewport")
            auto_fixes += 1

    # ---------------------------------------------------------
    # SAFE FIX 2: Missing title
    # ---------------------------------------------------------

    if not re.search(
        r"<title\b[^>]*>.*?</title>",
        content,
        re.I | re.S
    ):

        filename = path.stem.replace(
            "-",
            " "
        ).replace(
            "_",
            " "
        ).title()

        if re.search(
            r"<head\b[^>]*>",
            content,
            re.I
        ):

            content = re.sub(
                r"(<head\b[^>]*>)",
                r"\1\n    <title>" + filename + "</title>",
                content,
                count=1,
                flags=re.I
            )

            print(
                f"  AUTO-FIX: Added title: {filename}"
            )

            auto_fixes += 1

    # ---------------------------------------------------------
    # SAFE FIX 3: Missing alt attribute
    # ---------------------------------------------------------

    def fix_image(match):

        tag = match.group(0)

        if re.search(
            r"\balt\s*=",
            tag,
            re.I
        ):
            return tag

        return tag[:-1] + ' alt="">'

    new_content = re.sub(
        r"<img\b[^>]*>",
        fix_image,
        content,
        flags=re.I
    )

    if new_content != content:

        print(
            "  AUTO-FIX: Added missing image alt attributes"
        )

        auto_fixes += 1
        content = new_content

    if content != original:
        write_file(path, content)


def scan_page(path):

    global errors
    global warnings

    content = read_file(path)

    # ---------------------------------------------------------
    # Auto-fix safe problems first
    # ---------------------------------------------------------

    auto_fix_page(path)

    # Reload after possible fixes
    content = read_file(path)

    parser = PageParser()

    try:
        parser.feed(content)
    except Exception as exc:
        add_error(
            f"HTML parser error in {path}: {exc}"
        )
        return

    print(f"Checking: {path}")

    # ---------------------------------------------------------
    # Basic document structure
    # ---------------------------------------------------------

    if not re.search(
        r"<!doctype\s+html>",
        content,
        re.I
    ):
        add_warning(
            f"Missing HTML5 DOCTYPE in {path}"
        )

    if not re.search(
        r"<html\b",
        content,
        re.I
    ):
        add_error(
            f"Missing <html> tag in {path}"
        )

    if not re.search(
        r"<head\b",
        content,
        re.I
    ):
        add_error(
            f"Missing <head> tag in {path}"
        )

    if not re.search(
        r"<body\b",
        content,
        re.I
    ):
        add_error(
            f"Missing <body> tag in {path}"
        )

    # ---------------------------------------------------------
    # Language
    # ---------------------------------------------------------

    if not parser.lang:

        add_warning(
            "Missing lang attribute on <html>"
        )

    # ---------------------------------------------------------
    # Title
    # ---------------------------------------------------------

    if not parser.title:

        add_error(
            "Page has no usable <title>"
        )

    elif len(parser.title) > 70:

        add_warning(
            f"Title is long ({len(parser.title)} characters)"
        )

    # ---------------------------------------------------------
    # Meta description
    # ---------------------------------------------------------

    if not parser.description:

        add_warning(
            "Missing meta description"
        )

    elif len(parser.description) < 50:

        add_warning(
            f"Meta description is short ({len(parser.description)} characters)"
        )

    elif len(parser.description) > 170:

        add_warning(
            f"Meta description is long ({len(parser.description)} characters)"
        )

    # ---------------------------------------------------------
    # Canonical URL
    # ---------------------------------------------------------

    if not parser.canonical:

        add_warning(
            "Missing canonical URL"
        )

    # ---------------------------------------------------------
    # H1
    # ---------------------------------------------------------

    if parser.h1_count == 0:

        add_warning(
            "No <h1> heading found"
        )

    elif parser.h1_count > 1:

        add_warning(
            f"Multiple <h1> headings found ({parser.h1_count})"
        )

    # ---------------------------------------------------------
    # Duplicate IDs
    # ---------------------------------------------------------

    seen_ids = set()

    duplicate_ids = set()

    for item in parser.ids:

        if item in seen_ids:
            duplicate_ids.add(item)

        seen_ids.add(item)

    for duplicate in sorted(duplicate_ids):

        add_error(
            f"Duplicate HTML id: {duplicate}"
        )

    # ---------------------------------------------------------
    # Images without alt
    # ---------------------------------------------------------

    if parser.images_without_alt > 0:

        add_warning(
            f"{parser.images_without_alt} image(s) missing alt attribute"
        )

    # ---------------------------------------------------------
    # Broken links / files
    # ---------------------------------------------------------

    for reference_type, reference in parser.references:

        reference = reference.strip()

        if not reference:
            continue

        if reference.startswith("#"):
            continue

        if is_external(reference):
            continue

        target = resolve_local_file(
            path,
            reference
        )

        if target is None:
            continue

        if not target.exists():

            add_error(
                f"Missing referenced file: {reference}"
            )

    # ---------------------------------------------------------
    # Empty / invalid links
    # ---------------------------------------------------------

    if parser.links_without_href:

        add_warning(
            f"{parser.links_without_href} link(s) without href"
        )

    if parser.empty_links:

        add_warning(
            f"{parser.empty_links} empty link(s)"
        )

    # ---------------------------------------------------------
    # Navigation
    # ---------------------------------------------------------

    if not parser.has_nav:

        add_warning(
            "No <nav> element found"
        )

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    if not parser.has_footer:

        add_warning(
            "No <footer> element found"
        )

    # ---------------------------------------------------------
    # AdSense
    # ---------------------------------------------------------

    if not parser.has_adsense:

        print(
            "  INFO: No AdSense script detected"
        )

    # ---------------------------------------------------------
    # Closing report
    # ---------------------------------------------------------

    print()


def scan_duplicate_titles():

    global warnings

    print("-" * 70)
    print("CHECKING DUPLICATE PAGE TITLES")
    print("-" * 70)

    titles = {}

    for path in html_files:

        content = read_file(path)

        match = re.search(
            r"<title\b[^>]*>(.*?)</title>",
            content,
            re.I | re.S
        )

        if not match:
            continue

        title = re.sub(
            r"\s+",
            " ",
            match.group(1)
        ).strip().lower()

        if title:
            titles.setdefault(
                title,
                []
            ).append(path)

    for title, pages in titles.items():

        if len(pages) > 1:

            add_warning(
                "Duplicate title used by: "
                + ", ".join(
                    str(p) for p in pages
                )
            )

    print()


def scan_duplicate_descriptions():

    global warnings

    print("-" * 70)
    print("CHECKING DUPLICATE META DESCRIPTIONS")
    print("-" * 70)

    descriptions = {}

    for path in html_files:

        content = read_file(path)

        match = re.search(
            r'<meta\s+[^>]*name=["\']description["\'][^>]*content=["\']([^"\']*)["\']',
            content,
            re.I
        )

        if not match:
            continue

        description = re.sub(
            r"\s+",
            " ",
            match.group(1)
        ).strip().lower()

        if description:
            descriptions.setdefault(
                description,
                []
            ).append(path)

    for description, pages in descriptions.items():

        if len(pages) > 1:

            add_warning(
                "Duplicate meta description used by: "
                + ", ".join(
                    str(p) for p in pages
                )
            )

    print()


def scan_sitemap():

    global errors
    global warnings

    print("-" * 70)
    print("CHECKING SITEMAP")
    print("-" * 70)

    sitemap = ROOT / "sitemap.xml"

    if not sitemap.exists():

        add_error(
            "sitemap.xml is missing"
        )

        print()
        return

    content = read_file(sitemap)

    urls = re.findall(
        r"<loc>\s*(.*?)\s*</loc>",
        content,
        re.I | re.S
    )

    if not urls:

        add_error(
            "sitemap.xml contains no <loc> URLs"
        )

        print()
        return

    for url in urls:

        parsed = urlparse(url)

        if parsed.netloc.lower() != SITE_DOMAIN.lower():

            add_warning(
                f"Sitemap URL uses unexpected domain: {url}"
            )

            continue

        path = unquote(
            parsed.path
        )

        if path in ("", "/"):

            target = ROOT / "index.html"

        else:

            relative = path.lstrip("/")

            if relative.endswith("/"):
                relative += "index.html"

            target = ROOT / relative

            if not target.exists():

                if relative.endswith(".html"):

                    target = ROOT / relative

                else:

                    target = ROOT / (
                        relative + ".html"
                    )

        if not target.exists():

            add_error(
                f"Sitemap URL does not match a local page: {url}"
            )

    print(
        f"Sitemap URLs checked: {len(urls)}"
    )

    print()


def scan_robots():

    global warnings

    print("-" * 70)
    print("CHECKING ROBOTS.TXT")
    print("-" * 70)

    robots = ROOT / "robots.txt"

    if not robots.exists():

        add_warning(
            "robots.txt is missing"
        )

        print()
        return

    content = read_file(robots)

    if not re.search(
        r"User-agent\s*:",
        content,
        re.I
    ):

        add_warning(
            "robots.txt has no User-agent directive"
        )

    if not re.search(
        r"Sitemap\s*:",
        content,
        re.I
    ):

        add_warning(
            "robots.txt does not declare a sitemap"
        )

    print()


def scan_required_files():

    global warnings

    print("-" * 70)
    print("CHECKING REQUIRED SITE FILES")
    print("-" * 70)

    required = [
        "index.html",
        "404.html",
        "robots.txt",
        "sitemap.xml",
        "CNAME",
        "ads.txt",
    ]

    for filename in required:

        path = ROOT / filename

        if path.exists():

            print(
                f"  ✓ {filename}"
            )

        else:

            add_warning(
                f"Missing {filename}"
            )

    cname = ROOT / "CNAME"

    if cname.exists():

        domain = read_file(
            cname
        ).strip()

        if domain:

            print(
                f"  ✓ CNAME: {domain}"
            )

        else:

            add_error(
                "CNAME exists but is empty"
            )

    print()


def scan_advertising_files():

    global warnings

    print("-" * 70)
    print("CHECKING ADS.TXT")
    print("-" * 70)

    ads = ROOT / "ads.txt"

    if not ads.exists():

        add_warning(
            "ads.txt is missing"
        )

        print()
        return

    content = read_file(ads).strip()

    if not content:

        add_warning(
            "ads.txt is empty"
        )

    else:

        if "google.com" in content.lower():

            print(
                "  ✓ Google advertising entry detected"
            )

        else:

            print(
                "  INFO: No google.com entry detected in ads.txt"
            )

    print()


# =============================================================
# MAIN SCAN
# =============================================================

for html_file in html_files:

    scan_page(html_file)

scan_duplicate_titles()

scan_duplicate_descriptions()

scan_sitemap()

scan_robots()

scan_required_files()

scan_advertising_files()


# =============================================================
# FINAL REPORT
# =============================================================

print("=" * 70)
print("                         FINAL REPORT")
print("=" * 70)

print()
print(f"Pages scanned : {len(html_files)}")
print(f"Auto-fixes    : {auto_fixes}")
print(f"Warnings      : {warnings}")
print(f"Errors        : {errors}")
print()

if errors > 0:

    print("RESULT: FAILED")
    print()
    print(
        "The website has errors that should be fixed before pushing."
    )

    print(
        "Your pre-push hook will block the Git push."
    )

    print()

    sys.exit(1)

elif warnings > 0:

    print("RESULT: PASSED WITH WARNINGS")
    print()
    print(
        "No blocking errors were found."
    )

    print(
        "Review the warnings before publishing."
    )

    print()

    sys.exit(0)

else:

    print("RESULT: ALL CLEAR")
    print()
    print(
        "No errors or warnings detected."
    )

    print()

    sys.exit(0)

