from pathlib import Path
import re
from html.parser import HTMLParser

FILE = Path("contact.html")

ERRORS = []
WARNINGS = []

if not FILE.exists():
    print("ERROR: contact.html not found.")
    raise SystemExit(1)

html = FILE.read_text(encoding="utf-8")

class HTMLCheckParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.h1_count = 0
        self.title = ""
        self.meta_description = ""
        self.body_text = []
        self.script_locations = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        self.tags.append(tag)

        attrs_dict = dict(attrs)

        if tag == "h1":
            self.h1_count += 1

        if tag == "title":
            self.in_title = True

        if tag == "meta":
            if attrs_dict.get("name", "").lower() == "description":
                self.meta_description = attrs_dict.get("content", "")

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag == "title":
            self.in_title = False

        if tag in self.tags:
            for i in range(len(self.tags) - 1, -1, -1):
                if self.tags[i] == tag:
                    self.tags.pop(i)
                    break

    def handle_data(self, data):
        if self.in_title:
            self.title += data

        if data.strip():
            self.body_text.append(data.strip())

parser = HTMLCheckParser()
parser.feed(html)

# --------------------------------------------------
# BASIC HTML STRUCTURE
# --------------------------------------------------

if not re.search(r"<!DOCTYPE\s+html", html, re.I):
    ERRORS.append("Missing <!DOCTYPE html>")

for required in ["<html", "<head", "</head>", "<body", "</body>", "</html>"]:
    if required.lower() not in html.lower():
        ERRORS.append(f"Missing required HTML structure: {required}")

# --------------------------------------------------
# TITLE
# --------------------------------------------------

title = parser.title.strip()

if not title:
    ERRORS.append("Missing <title>")

elif len(title) > 70:
    WARNINGS.append(f"Title is long ({len(title)} characters)")

# --------------------------------------------------
# META DESCRIPTION
# --------------------------------------------------

description = parser.meta_description.strip()

if not description:
    ERRORS.append("Missing meta description")

elif len(description) < 120:
    WARNINGS.append(
        f"Meta description is short ({len(description)} characters)"
    )

elif len(description) > 170:
    WARNINGS.append(
        f"Meta description is long ({len(description)} characters)"
    )

# --------------------------------------------------
# VIEWPORT
# --------------------------------------------------

if not re.search(
    r'<meta[^>]+name=["\']viewport["\'][^>]+content=',
    html,
    re.I
):
    ERRORS.append("Missing mobile viewport")

# --------------------------------------------------
# CANONICAL
# --------------------------------------------------

canonical = re.search(
    r'<link[^>]+rel=["\']canonical["\'][^>]+href=["\']([^"\']+)',
    html,
    re.I
)

expected_canonical = "https://kinglee6mutwiri.co.ke/contact.html"

if not canonical:
    ERRORS.append("Missing canonical URL")
elif canonical.group(1) != expected_canonical:
    ERRORS.append(
        f"Wrong canonical URL: {canonical.group(1)}"
    )

# --------------------------------------------------
# H1
# --------------------------------------------------

if parser.h1_count == 0:
    ERRORS.append("No H1 found")

elif parser.h1_count > 1:
    ERRORS.append(
        f"Multiple H1 headings found ({parser.h1_count})"
    )

# --------------------------------------------------
# GOOGLE ANALYTICS
# --------------------------------------------------

if "G-S8VF9QWKET" not in html:
    ERRORS.append("GA4 ID G-S8VF9QWKET not found")

# --------------------------------------------------
# ADSENSE
# --------------------------------------------------

if "adsbygoogle" in html.lower() or "ca-pub-" in html.lower():
    ERRORS.append("AdSense code found - Contact page should have NO AdSense")

# --------------------------------------------------
# AUTHOR IMAGE
# --------------------------------------------------

author_image = "images/perfect_laptop_d1b8df7b.jpg"

if author_image not in html:
    ERRORS.append("Author image not found")

# --------------------------------------------------
# REQUIRED NAVIGATION / INTERNAL LINKS
# --------------------------------------------------

required_links = {
    "Homepage": "https://kinglee6mutwiri.co.ke/",
    "About": "https://kinglee6mutwiri.co.ke/about.html",
    "Contact": "https://kinglee6mutwiri.co.ke/contact.html",
    "Privacy Policy": "https://kinglee6mutwiri.co.ke/privacy-policy.html",
    "Terms": "https://kinglee6mutwiri.co.ke/terms.html",
    "Disclaimer": "https://kinglee6mutwiri.co.ke/disclaimer.html",
    "Muscle article": "https://kinglee6mutwiri.co.ke/how-to-build-muscle.html",
    "Child article": "https://kinglee6mutwiri.co.ke/your-child-may-not-say-it.html",
    "Money article": "https://kinglee6mutwiri.co.ke/the-man-who-earned-more-money-but-became-poorer.html",
}

for name, link in required_links.items():
    if link not in html:
        ERRORS.append(f"Missing internal link: {name}")

# --------------------------------------------------
# CONTACT DETAILS
# --------------------------------------------------

if "kinglee6mutwiri@gmail.com" not in html:
    ERRORS.append("Email address missing")

if "https://wa.me/254798783620" not in html:
    ERRORS.append("WhatsApp link missing")

if "tel:+254798783620" not in html:
    ERRORS.append("Phone link missing")

# --------------------------------------------------
# SOCIAL LINKS
# --------------------------------------------------

social_links = {
    "Facebook": "https://www.facebook.com/profile.php?id=61568056696688",
    "Instagram": "https://www.instagram.com/mutwiri.eliphas/",
    "X": "https://x.com/KingleeMut40701",
}

for name, link in social_links.items():
    if link not in html:
        WARNINGS.append(f"{name} social link not found")

# --------------------------------------------------
# FAQ
# --------------------------------------------------

if not re.search(r"<h2[^>]*>.*FAQ|Frequently Asked Questions", html, re.I | re.S):
    ERRORS.append("FAQ section not found")

# --------------------------------------------------
# FOOTER
# --------------------------------------------------

if "<footer" not in html.lower() or "</footer>" not in html.lower():
    ERRORS.append("Footer missing")

# --------------------------------------------------
# PLACEHOLDER LINKS
# --------------------------------------------------

placeholder_patterns = [
    'href="#"',
    'href=""',
    'href="javascript:',
    "href='#'",
    "href=''",
]

for pattern in placeholder_patterns:
    if pattern.lower() in html.lower():
        ERRORS.append(f"Placeholder link found: {pattern}")

# --------------------------------------------------
# OLD / UNWANTED WORDING
# --------------------------------------------------

if re.search(r"america[\s-]*ai", html, re.I):
    ERRORS.append("Unwanted old site wording found")

# --------------------------------------------------
# SCRIPT PLACEMENT
# --------------------------------------------------

head_match = re.search(
    r"<head\b.*?</head>",
    html,
    re.I | re.S
)

body_match = re.search(
    r"<body\b.*?</body>",
    html,
    re.I | re.S
)

head_content = head_match.group(0) if head_match else ""
body_content = body_match.group(0) if body_match else ""

all_scripts = re.findall(
    r"<script\b.*?</script>",
    html,
    re.I | re.S
)

for script in all_scripts:
    if script not in head_content and script not in body_content:
        ERRORS.append("SCRIPT tag found outside HEAD/BODY")

# --------------------------------------------------
# WORD COUNT
# --------------------------------------------------

clean_text = re.sub(r"<script\b.*?</script>", " ", html, flags=re.I | re.S)
clean_text = re.sub(r"<style\b.*?</style>", " ", clean_text, flags=re.I | re.S)
clean_text = re.sub(r"<[^>]+>", " ", clean_text)
clean_text = re.sub(r"&[a-zA-Z0-9#]+;", " ", clean_text)

words = re.findall(r"\b[\w’'-]+\b", clean_text, re.UNICODE)
word_count = len(words)

if word_count < 2500:
    WARNINGS.append(
        f"Page is under 2,500 words ({word_count})"
    )

# --------------------------------------------------
# RESULT
# --------------------------------------------------

print()
print("=" * 55)
print("KINGLEE6 CONTACT PAGE CHECK")
print("=" * 55)
print()
print(f"FILE       : {FILE}")
print(f"WORD COUNT : {word_count}")
print(f"ERRORS     : {len(ERRORS)}")
print(f"WARNINGS   : {len(WARNINGS)}")
print()

if ERRORS:
    print("ERROR DETAILS:")
    for error in ERRORS:
        print(f" - {error}")
else:
    print("ERROR DETAILS:")
    print(" - None")

print()

if WARNINGS:
    print("WARNING DETAILS:")
    for warning in WARNINGS:
        print(f" - {warning}")
else:
    print("WARNING DETAILS:")
    print(" - None")

print()
print("=" * 55)

if not ERRORS:
    print("RESULT: PASS - No errors found.")
else:
    print("RESULT: FIX ERRORS BEFORE PUSHING.")

print("=" * 55)
