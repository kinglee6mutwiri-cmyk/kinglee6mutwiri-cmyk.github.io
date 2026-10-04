from bs4 import BeautifulSoup

file = "your-child-may-not-say-it.html"

with open(file, "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

print("\nSCRIPT LOCATIONS:\n")

for i, script in enumerate(soup.find_all("script"), 1):
    parent = script.parent.name if script.parent else "NONE"

    src = script.get("src", "")
    if src:
        info = src
    else:
        info = "inline script"

    print(f"{i}. Parent: <{parent}> | {info}")

print("\nRAW SCRIPT POSITIONS:\n")

for i, match in enumerate(
    __import__("re").finditer(r"<script\b", html, __import__("re").I),
    1
):
    position = match.start()

    before = html[:position].lower()

    last_head = before.rfind("</head>")
    last_body = before.rfind("</body>")
    last_head_open = before.rfind("<head")
    last_body_open = before.rfind("<body")

    if last_head > last_body and last_head > last_head_open:
        location = "AFTER HEAD / BEFORE BODY"
    elif last_body > last_body_open:
        location = "AFTER BODY"
    elif last_body_open > last_head:
        location = "INSIDE BODY"
    elif last_head_open > last_body:
        location = "INSIDE HEAD"
    else:
        location = "UNKNOWN"

    print(f"{i}. {location}")

print("\nDone.")
