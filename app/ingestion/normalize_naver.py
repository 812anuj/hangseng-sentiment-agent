
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta

RAW_PATH = Path("data/raw/naver_posts.json")
OUTPUT_PATH = Path("data/processed/naver_cleaned.json")

def convert_to_utc(timestamp):
    """Convert a timestamp into UTC."""

    if not timestamp:
        return None

    dt = datetime.fromisoformat(
        timestamp.replace("Z", "+00:00")
    )

    # If timezone is missing, assume Korea Standard Time.
    if dt.tzinfo is None:
        korea_timezone = timezone(timedelta(hours=9))
        dt = dt.replace(tzinfo=korea_timezone)

    return dt.astimezone(timezone.utc).isoformat()

def clean_text(value):
    """Remove unnecessary whitespace."""

    if not value:
        return ""

    return " ".join(str(value).split())

def normalize_naver_posts():

    with RAW_PATH.open("r", encoding="utf-8") as file:
        raw_posts = json.load(file)

    cleaned_posts = []
    seen_ids = set()

    for post in raw_posts:

        post_id = str(post.get("postId", ""))

        # Skip duplicate posts.
        if not post_id or post_id in seen_ids:
            continue

        title = clean_text(post.get("title"))
        text = clean_text(post.get("text"))

        # Skip records without meaningful content.
        if not title and not text:
            continue

        seen_ids.add(post_id)

        cleaned_post = {
            "post_id": f"naver_{post_id}",
            "ticker": post.get("ticker") or post.get("stockCode"),
            "company": post.get("company") or post.get("stockName"),
            "exchange": "South Korea",
            "asset_scope": "stock",
            "record_type": "post",
            "title": title,
            "text": text,
            "source": "Naver Finance",
            "author": post.get("author"),
            "timestamp_utc": convert_to_utc(
                post.get("writtenAt")
            ),
            "likes": int(post.get("likes") or 0),
            "comments": 0,
            "shares": 0,
            "views": int(post.get("views") or 0),
            "dislikes": int(post.get("dislikes") or 0),
            "author_followers": None,
            "is_holder_verified": post.get(
                "isHolderVerified", False
            ),
            "url": post.get("url")
        }

        cleaned_posts.append(cleaned_post)

    OUTPUT_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(
            cleaned_posts,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("Naver normalization completed!")
    print("Raw records:", len(raw_posts))
    print("Clean records:", len(cleaned_posts))
    print("Removed records:", len(raw_posts) - len(cleaned_posts))
    print("Saved to:", OUTPUT_PATH)

    if cleaned_posts:
        print("\nFirst normalized post:")
        print(
            json.dumps(
                cleaned_posts[0],
                ensure_ascii=False,
                indent=4
            )
        )

if __name__ == "__main__":
    normalize_naver_posts()