import re

file = "your-child-may-not-say-it.html"

with open(file, "r", encoding="utf-8") as f:
    html = f.read()

# 1. Shorten title only
html = re.sub(
    r"<title>.*?</title>",
    "<title>Your Child May Not Say It: What Parents Should Know | Kinglee6</title>",
    html,
    count=1,
    flags=re.I | re.S
)

# 2. Shorten meta description only
html = re.sub(
    r'(<meta\s+name=["\']description["\']\s+content=["\']).*?(["\'])',
    r'\1Children do not always have words for their feelings. Learn to notice behaviour, listen carefully, build trust and support your child.\2',
    html,
    count=1,
    flags=re.I | re.S
)

# 3. Move scripts that are outside BODY into BODY
body_match = re.search(r"</body\s*>", html, flags=re.I)

if body_match:
    body_end = body_match.start()

    before_body_end = html[:body_end]
    after_body_end = html[body_end:]

    # Find script blocks located after </body>
    scripts = re.findall(
        r"<script\b[^>]*>.*?</script\s*>",
        after_body_end,
        flags=re.I | re.S
    )

    # Remove only those stray scripts from after </body>
    for script in scripts:
        after_body_end = after_body_end.replace(script, "", 1)

    # Put the stray scripts immediately before </body>
    if scripts:
        clean_scripts = "\n".join(scripts)
        html = before_body_end.rstrip() + "\n\n" + clean_scripts + "\n" + after_body_end.lstrip()

# 4. Save the corrected page
with open(file, "w", encoding="utf-8") as f:
    f.write(html)

print("FIX COMPLETE")
print("Content was not rewritten.")
print("Title and meta description shortened.")
print("Stray scripts moved inside BODY.")
