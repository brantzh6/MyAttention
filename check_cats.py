import json

with open(r"c:\Users\Jiu You\code\MyAttention\feeds_test.json", encoding="utf-8") as f:
    data = json.load(f)

cats = {}
sources = {}
for item in data:
    cat = item.get("category", "unknown")
    src = item.get("source", "unknown")
    cats[cat] = cats.get(cat, 0) + 1
    sources[src] = sources.get(src, 0) + 1

print("=== Categories ===")
for k, v in sorted(cats.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print("\n=== Sources ===")
for k, v in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {k}: {v}")

print(f"\nTotal: {len(data)}")
