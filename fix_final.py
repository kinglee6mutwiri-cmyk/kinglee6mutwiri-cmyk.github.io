import re, pathlib
p = pathlib.Path("index.html")
html = p.read_text(encoding="utf-8")

# 1. UNDO bad defer injection
html = html.replace('<script defer', '<script')
html = re.sub(r'defer defer', 'defer', html)
html = re.sub(r'<style>.post-card.*?</style>', '', html, flags=re.S)
html = re.sub(r'<link rel="preload"[^>]+as="image"[^>]*>', '', html)

# 2. FIX Best Practices 81 -> 100
# add rel=noopener to all _blank
html = re.sub(r'target="_blank"(?![^>]*rel=)', 'target="_blank" rel="noopener"', html)
# remove http:// links if any
html = html.replace('http://kinglee6mutwiri.co.ke', 'https://kinglee6mutwiri.co.ke')
# ensure all img have alt
html = re.sub(r'<img(?![^>]*alt=)', '<img alt="Kinglee Mutwiri story"', html)

# 3. FIX Performance Mobile 73 -> 90+
# Find hero image - make it high priority, others lazy
count = [0]
def fix_img(m):
    count[0]+=1
    tag = m.group(0)
    tag = re.sub(r'\s+loading="[^"]+"', '', tag)
    tag = re.sub(r'\s+fetchpriority="[^"]+"', '', tag)
    if count[0]==1:
        # hero - keep eager, add width height + fetchpriority
        if 'width=' not in tag:
            tag = tag.replace('<img', '<img width="1200" height="675" fetchpriority="high" decoding="async"')
        # add preload in head later
        return tag
    else:
        # rest lazy
        tag = tag.replace('<img', '<img loading="lazy" decoding="async" width="400" height="225"', 1)
        return tag

html = re.sub(r'<img[^>]+>', fix_img, html, flags=re.I)

# Add preload for first image
m = re.search(r'<img[^>]+src="([^"]+)"', html, re.I)
if m:
    first_src = m.group(1)
    preload_tag = f'<link rel="preload" as="image" href="{first_src}" fetchpriority="high">\n'
    html = html.replace('</head>', preload_tag + '</head>')

# Defer only external JS, not inline
html = re.sub(r'<script src="([^"]+)"></script>', r'<script src="\1" defer></script>', html)

p.write_text(html, encoding="utf-8")
print(f"Fixed {count[0]} images. Best Practices should be 100 again.")
