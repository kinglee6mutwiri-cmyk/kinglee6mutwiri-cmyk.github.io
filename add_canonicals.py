from pathlib import Path

DOMAIN = "https://kinglee6mutwiri.co.ke"

pages = {
    "404.html": "/404.html",
    "about.html": "/about.html",
    "index.html": "/",
    "lil-wayne.html": "/lil-wayne.html",
    "lucky-dube.html": "/lucky-dube.html",
    "martin-luther-king-jr.html": "/martin-luther-king-jr.html",
    "muhammad-ali.html": "/muhammad-ali.html",
    "nelson-mandela.html": "/nelson-mandela.html",
    "pop-smoke.html": "/pop-smoke.html",
    "rihanna.html": "/rihanna.html",
    "salary-disappeared-story.html": "/salary-disappeared-story.html",
    "the-man-who-earned-more-money-but-became-poorer.html": "/the-man-who-earned-more-money-but-became-poorer.html",
}

for filename, path in pages.items():
    file = Path(filename)

    if not file.exists():
        print(f"SKIPPED: {filename} does not exist")
        continue

    html = file.read_text(encoding="utf-8")

    if 'rel="canonical"' in html:
        print(f"ALREADY OK: {filename}")
        continue

    canonical = f'<link rel="canonical" href="{DOMAIN}{path}">'

    if "</head>" not in html.lower():
        print(f"SKIPPED: {filename} has no </head>")
        continue

    position = html.lower().find("</head>")

    html = html[:position] + canonical + "\n" + html[position:]

    file.write_text(html, encoding="utf-8")

    print(f"ADDED: {filename} -> {DOMAIN}{path}")

print("\nCanonical URL update complete.")

