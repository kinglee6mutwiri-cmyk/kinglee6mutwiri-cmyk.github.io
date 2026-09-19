import os
for root, dirs, files in os.walk("."):
    for f in files:
        if f.endswith(".html"):
            path = os.path.join(root, f)
            with open(path, 'r', encoding='utf-8', errors='ignore') as file:
                data = file.read()
            if 'ad-wrap" aria-label' in data:
                new = data.replace('<div class="ad-wrap" aria-label="Advertisement">', '<div class="ad-wrap" role="complementary" aria-label="Advertisement">')
                with open(path, 'w', encoding='utf-8') as file:
                    file.write(new)
                print(f"Fixed {path}")
print("DONE")
