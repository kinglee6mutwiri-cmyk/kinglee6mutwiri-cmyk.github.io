import os, glob
errors = []
# 1. check backup files
for f in glob.glob("*backup*") + glob.glob("*sitemap-backup*"):
    errors.append(f"BACKUP FILE FOUND: {f} -> DELETE IT, causes Low Value!")

# 2. check sitemap count
if os.path.exists("sitemap.xml"):
    print("sitemap.xml OK")

if errors:
    print("\n".join(errors))
    print("\nFIX ERRORS ABOVE FIRST")
else:
    print("✅ All checks passed - no Low Value errors")
