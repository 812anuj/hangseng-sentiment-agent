
import json
from pathlib import Path


# --------------------------------------------------
# 1. File paths
# --------------------------------------------------

INPUT_PATH = Path("data/raw/lihkg_thread_details.json")

OUTPUT_PATH = Path("data/processed/lihkg_cleaned.json")


# --------------------------------------------------
# 2. Normalize one LIHKG record
# --------------------------------------------------

def normalize_lihkg_record(raw_record, parent_title=None):

    is_reply = "reply_id" in raw_record

    text = (
        raw_record.get("own_text")
        or raw_record.get("content")
        or ""
    )

    post = {

        "post_id": (
            f"reply_{raw_record.get('reply_id')}"
            if is_reply
            else f"thread_{raw_record.get('thread_id')}"
        ),

        "thread_id": raw_record.get("thread_id"),

        "record_type": (
            "reply" if is_reply else "thread"
        ),

        "ticker": None,
        "company": None,

        "exchange": "Hong Kong",
        "asset_scope": "market",

        "title": raw_record.get("title") or parent_title,

        "source": "LIHKG",

        "author": raw_record.get("author"),

        "text": text.strip(),

        "likes": raw_record.get("like_count", 0),
        "dislikes": raw_record.get("dislike_count", 0),

        "shares": 0,
        "author_followers": None,

        "thread_reply_count": raw_record.get("reply_count"),

        "timestamp_utc": raw_record.get("created_at"),

        "url": (
            raw_record.get("thread_url")
            or raw_record.get("url")
        )
    }

    return post


# --------------------------------------------------
# 3. Load raw data
# --------------------------------------------------

def load_raw_data():

    if not INPUT_PATH.exists():
        raise FileNotFoundError(
            f"Raw data file not found: {INPUT_PATH}"
        )

    with INPUT_PATH.open("r", encoding="utf-8") as file:
        return json.load(file)


# --------------------------------------------------
# 4. Normalize all records
# --------------------------------------------------

def normalize_all_posts(raw_data):

    normalized_posts = []

    # Build a dictionary containing thread titles
    thread_titles = {}

    for record in raw_data:

        if "reply_id" not in record:

            thread_id = record.get("thread_id")

            thread_titles[thread_id] = record.get("title")

    # Normalize threads and replies
    for raw_record in raw_data:

        thread_id = raw_record.get("thread_id")

        parent_title = thread_titles.get(thread_id)

        normalized_post = normalize_lihkg_record(
            raw_record,
            parent_title
        )

        normalized_posts.append(normalized_post)

    return normalized_posts


# --------------------------------------------------
# 5. Clean records
# --------------------------------------------------

def clean_posts(posts):

    cleaned_posts = []

    seen_ids = set()

    for post in posts:

        # Remove empty text
        if not post["text"]:
            continue

        # Remove duplicate records
        if post["post_id"] in seen_ids:
            continue

        seen_ids.add(post["post_id"])

        cleaned_posts.append(post)

    return cleaned_posts


# --------------------------------------------------
# 6. Validate records
# --------------------------------------------------

def validate_posts(posts):

    thread_count = 0
    reply_count = 0

    for post in posts:

        if post["record_type"] == "thread":
            thread_count += 1

        elif post["record_type"] == "reply":
            reply_count += 1

    print("\n========== DATA VALIDATION ==========")

    print("Total records:", len(posts))
    print("Threads:", thread_count)
    print("Replies:", reply_count)

    print(
        "Records with missing text:",
        sum(1 for post in posts if not post["text"])
    )

    print(
        "Records with missing timestamps:",
        sum(1 for post in posts if not post["timestamp_utc"])
    )


# --------------------------------------------------
# 7. Save cleaned data
# --------------------------------------------------

def save_cleaned_data(posts):

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:

        json.dump(
            posts,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\nCleaned data saved:", OUTPUT_PATH)


# --------------------------------------------------
# 8. Main execution
# --------------------------------------------------

if __name__ == "__main__":

    raw_data = load_raw_data()

    print("Total raw records:", len(raw_data))

    normalized_posts = normalize_all_posts(raw_data)

    print("Total normalized records:", len(normalized_posts))

    cleaned_posts = clean_posts(normalized_posts)

    validate_posts(cleaned_posts)

    print(
        "\nRecords removed:",
        len(normalized_posts) - len(cleaned_posts)
    )

    if cleaned_posts:

        print("\nFirst cleaned record:")
        print(cleaned_posts[0])

        print("\nFirst cleaned reply:")

        first_reply = next(
            (
                post for post in cleaned_posts
                if post["record_type"] == "reply"
            ),
            None
        )

        print(first_reply)

    save_cleaned_data(cleaned_posts)
