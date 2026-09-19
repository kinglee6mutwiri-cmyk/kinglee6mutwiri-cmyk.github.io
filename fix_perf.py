import re, pathlib

p = pathlib.Path("index.html")
html = p.read_text(encoding="utf-8")

# 1. Preload LCP hero image - find first big image
imgs = re.findall(r'<img[^>]+src="([^"]+)"', html, re.I)
if imgs:
    lcp = imgs[0]
    if 'rel="preload"' not in html:
        preload = f'<link rel="preload" as="image" href="{lcp}" fetchpriority="high">\n'
        html = html.replace("</head>", preload + "</head>")
        print(f"Preloaded LCP: {lcp}")

# 2. Add lazy loading to all images except first 2
count = 0
def add_lazy(m):
    global count
    count += 1
    tag = m.group(0)
    if count <= 2:
        # first images = high priority
        if 'fetchpriority' not in tag:
            tag = tag.replace('<img', '<img fetchpriority="high" decoding="async"', 1)
        return tag
    if 'loading=' not in tag:
        tag = tag.replace('<img', '<img loading="lazy" decoding="async"', 1)
    if 'width=' not in tag:
        tag = tag.replace('<img', '<img width="800" height="450"', 1)
    return tag

html = re.sub(r'<img[^>]+>', add_lazy, html, flags=re.I)

# 3. Defer all scripts
html = re.sub(r'<script', '<script defer', html)
html = html.replace('defer defer', 'defer') # fix double

# 4. Add viewport already there, but ensure content-visibility for sections
html = html.replace('</body>', '<style>.post-card{content-visibility:auto;contain-intrinsic-size:300px}</style></body>')

p.write_text(html, encoding="utf-8")
print(f"Fixed {count} images, added defer, preload")
print("DONE - Now push")
