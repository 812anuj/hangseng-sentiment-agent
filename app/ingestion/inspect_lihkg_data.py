import json

with open("data/raw/dataset_lihkg-scraper-en_2026-11-10_13-41-29-613.json", "r", encoding="utf-8") as file:
    data = json.load(file)
    print("Data type:", type(data))

if isinstance(data, list):
    print("Number of posts:", len(data))

    print("\nFirst post:")
    print(data[0])

    print("\nAvailable fields:")
    print(data[0].keys())

elif isinstance(data, dict):
    print("\nAvailable fields:")
    print(data.keys())


print("\n========== INSPECTING FIRST 3 RECORDS ==========")

for index, post in enumerate(data[:3], start=1):

    print(f"\nRecord number: {index}")

    print("Thread ID:", post.get("thread_id"))
    print("Title:", post.get("title"))

    print("Author:", post.get("author"))

    print(
        "Text:",
        (post.get("own_text") or post.get("content") or "")[:200]
    )

    print("Created at:", post.get("created_at"))

    print("Available fields:", list(post.keys()))

