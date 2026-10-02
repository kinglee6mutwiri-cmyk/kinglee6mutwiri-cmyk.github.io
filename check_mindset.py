from pathlib import Path
from html.parser import HTMLParser
import re

file = Path("mindset-and-life.html")

if not file.exists():
    print("ERROR: mindset-and-life.html not found")
    raise SystemExit(1)

html = file.read_text(encoding="utf-8", errors="replace")

errors = []
warnings = []


class Checker(HTMLParser):

    void_tags = {
        "area", "base", "br", "col", "embed", "hr",
        "img", "input", "link", "meta", "param",
        "source", "track", "wbr"
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.ids = set()
        self.images = []
        self.links = []

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs = dict(attrs)

        if tag not in self.void_tags:
            self.stack.append(tag)

        if "id" in attrs:
            ident = attrs["id"]
            if ident in self.ids:
                errors.append("Duplicate ID: " + ident)
            self.ids.add(ident)

        if tag == "img":
            self.images.append(attrs)

            if not attrs.get("src"):
                errors.append("Image has no src")

            if not attrs.get("alt"):
                warnings.append("Image has no alt text")

        if tag == "a":
            self.links.append(attrs)

            if not attrs.get("href"):
                errors.append("Link has no href")

    def handle_endtag(self, tag):
        tag = tag.lower()

        if tag in self.void_tags:
            return

        if not self.stack:
            errors.append("Unexpected closing tag: </" + tag + ">")
            return

        if self.stack[-1] != tag:
            errors.append(
                "Mismatched tag: expected </"
                + self.stack[-1]
                + "> but found </"
                + tag
                + ">"
            )
        else:
            self.stack.pop()

    def close(self):
        super().close()

        for tag in reversed(self.stack):
            errors.append("Unclosed tag: <" + tag + ">")


checker = Checker()

try:
    checker.feed(html)
    checker.close()
except Exception as e:
    errors.append("HTML parser error: " + str(e))


def count_tag(tag):
    return len(re.findall(r"<" + tag + r"\b", html, re.IGNORECASE))


# Remove CSS and JavaScript before counting words
clean = re.sub(
    r"<script\b.*?</script>",
    " ",
    html,
    flags=re.IGNORECASE | re.DOTALL
)

clean = re.sub(
    r"<style\b.*?</style>",
    " ",
    clean,
    flags=re.IGNORECASE | re.DOTALL
)

clean = re.sub(r"<[^>]+>", " ", clean)

words = re.findall(r"\b[\w'-]+\b", clean)


# Basic checks

if not re.search(r"<!DOCTYPE\s+html", html, re.IGNORECASE):
    errors.append("Missing DOCTYPE")

if not re.search(r"<title>.+?</title>", html, re.IGNORECASE | re.DOTALL):
    errors.append("Missing or empty title")

if "author-v2.webp" in html:
    errors.append("Old author image reference still exists")

if "America AI" in html:
    errors.append("Forbidden text found")

if count_tag("h1") != 1:
    warnings.append(
        "H1 count is " + str(count_tag("h1")) + "; expected 1"
    )

if len(checker.images) != 1:
    warnings.append(
        "Image count is " + str(len(checker.images)) + "; expected 1"
    )

if not re.search(
    r'name=["\']viewport["\']',
    html,
    re.IGNORECASE
):
    warnings.append("Viewport meta tag missing")

if not re.search(
    r'name=["\']description["\']',
    html,
    re.IGNORECASE
):
    warnings.append("Meta description missing")

if not re.search(
    r'rel=["\']canonical["\']',
    html,
    re.IGNORECASE
):
    warnings.append("Canonical URL missing")

if "G-X3HE9CKP90" not in html:
    warnings.append("GA4 ID not found")

if "ca-pub-5799841502846177" not in html:
    warnings.append("AdSense client ID not found")


# Check local image files

for image in checker.images:
    src = image.get("src", "")

    if src and not src.startswith(("http://", "https://", "data:", "//")):
        image_path = file.parent / src.split("?")[0].split("#")[0]

        if not image_path.exists():
            errors.append("Broken image: " + src)


print()
print("=" * 60)
print("MINDSET & LIFE — FULL CHECK")
print("=" * 60)

print()
print("WORD COUNT :", len(words))
print("IMAGES     :", len(checker.images))
print("H1         :", count_tag("h1"))
print("H2         :", count_tag("h2"))
print("H3         :", count_tag("h3"))
print("LINKS      :", len(checker.links))
print("UNIQUE IDs :", len(checker.ids))

print()
print("--- ERRORS ---")

if errors:
    for error in errors:
        print("ERROR:", error)
else:
    print("NONE")

print()
print("--- WARNINGS ---")

if warnings:
    for warning in warnings:
        print("WARNING:", warning)
else:
    print("NONE")

print()
print("=" * 60)
print("TOTAL ERRORS   :", len(errors))
print("TOTAL WARNINGS :", len(warnings))
print("=" * 60)

if errors:
    print("STATUS: ERRORS FOUND")
elif warnings:
    print("STATUS: NO ERRORS, WARNINGS FOUND")
else:
    print("STATUS: CLEAN — NO ERRORS OR WARNINGS")
