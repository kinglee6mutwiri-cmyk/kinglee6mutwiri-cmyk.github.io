file = "mindset-and-life.html"

with open(file, "r", encoding="utf-8") as f:
    content = f.read()

# Fix the heading skip error at line 1040
content = content.replace("<h4>Luck", "<h3>Luck")
content = content.replace("<h4> Luck", "<h3> Luck")

# Also fix closing tag if it's </h4> for that section
# This will fix only the first occurrence near Luck
content = content.replace("<h3>Luck a</h4>", "<h3>Luck a</h3>")

with open(file, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed: h4 -> h3 for Luck heading")
