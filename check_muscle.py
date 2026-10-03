from bs4 import BeautifulSoup
import re
import os

FILE = "how-to-build-muscle.html"

errors = 0
warnings = 0

def error(message):
    global errors
    errors += 1
    print(f"ERROR: {message}")

def warning(message):
    global warnings
    warnings += 1
    print(f"WARNING: {message}")

def passed(message):
    print(f"PASS: {message}")

print("=" * 60)
print("KINGLEE6 PAGE CHECK")
print("=" * 60)

if not os.path.exists(FILE):
    error(f"{FILE} not found")
else:
    with open(FILE, encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")

    # WORD COUNT
    content = BeautifulSoup(html, "html.parser")
    for tag in content(["script", "style", "nav", "footer"]):
        tag.decompose()

    text = " ".join(content.stripped_strings)
    word_count = len(re.findall(r"\b[\w’'-]+\b", text))

    print(f"\nWORDS: {word_count}")

    if word_count >= 2500:
        passed("Word count is 2,500+")
    else:
        warning(f"Word count is below 2,500 ({word_count})")

    # BASIC HTML
    print("\n===== HTML / SEO =====")

    if re.search(r"<!DOCTYPE\s+html", html, re.I):
        passed("DOCTYPE")
    else:
        error("DOCTYPE missing")

    if soup.find("meta", attrs={"name": "viewport"}):
        passed("Viewport")
    else:
        error("Viewport missing")

    if soup.find("link", attrs={"rel": "canonical"}):
        passed("Canonical")
    else:
        warning("Canonical missing")

    if soup.title:
        passed("Title")
    else:
        error("Title missing")

    if soup.find("meta", attrs={"name": "description"}):
        passed("Meta description")
    else:
        warning("Meta description missing")

    # H1
    h1 = soup.find_all("h1")

    print("\n===== HEADINGS =====")

    if len(h1) == 1:
        passed("Exactly 1 H1")
    elif len(h1) == 0:
        error("No H1")
    else:
        error(f"{len(h1)} H1 headings found")

    print(f"H2: {len(soup.find_all('h2'))}")
    print(f"H3: {len(soup.find_all('h3'))}")

    # GA4
    print("\n===== ANALYTICS =====")

    if "G-S8VF9QWKET" in html:
        passed("GA4")
    else:
        warning("GA4 ID missing")

    # ADSENSE
    print("\n===== ADSENSE =====")

    if "ca-pub-5799841502846177" in html:
        passed("AdSense client")
    else:
        error("AdSense client missing")

    if "pagead2.googlesyndication.com/pagead/js" in html:
        passed("AdSense loader")
    else:
        error("AdSense loader missing")

    if "6388196362" in html:
        passed("Top ad slot")
    else:
        warning("Top ad slot missing")

    if "1217574823" in html:
        passed("In-article ad slot")
    else:
        warning("In-article ad slot missing")

    # IMAGE
    print("\n===== IMAGES =====")

    if "images/author-muscle.jpg" in html:
        passed("Author image")
    else:
        warning("Author image missing")

    if len(soup.find_all("img")) > 0:
        passed(f"{len(soup.find_all('img'))} image(s) found")
    else:
        warning("No images found")

    # LINKS
    print("\n===== LINKS =====")

    links = soup.find_all("a", href=True)
    print(f"Total links: {len(links)}")

    if len(links) > 0:
        passed("Links found")
    else:
        warning("No links found")

    # FORBIDDEN TEXT
    print("\n===== CONTENT CHECK =====")

    if re.search(r"America\s*-?\s*AI", html, re.I):
        error("Forbidden 'America AI' text found")
    else:
        passed("No 'America AI' text")

    for term in ["TODO", "FIXME", "Lorem ipsum", "placeholder"]:
        if term.lower() in html.lower():
            warning(f"'{term}' found")

    # FINAL SUMMARY
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)

    print(f"ERRORS:   {errors}")
    print(f"WARNINGS: {warnings}")

    if errors == 0 and warnings == 0:
        print("STATUS:   PERFECT — NO ERRORS OR WARNINGS")
    elif errors == 0:
        print("STATUS:   PASS — NO ERRORS")
        print("          Review the warnings above.")
    else:
        print("STATUS:   FIX ERRORS")

    print("=" * 60)
