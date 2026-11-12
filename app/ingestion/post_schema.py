post = {
    "post_id": "example_001",

    # Stock information
    "ticker": "0700.HK",
    "company": "Tencent",
    "exchange": "Hong Kong",

    # Where the post came from
    "source": "Telegram",

    # When the post was published (UTC)
    "timestamp_utc": "2026-11-09T08:30:00Z",

    # Actual post content
    "text": "Tencent may rise next week because its AI business is growing.",

    # Engagement information
    "likes": 120,
    "comments": 15,
    "shares": 8,
    "author_followers": 2500,

    # Original post link, if available
    "url": None
}

for key, value in post.items():
    print(f"{key}: {value}")

posts = [
    {
        "ticker": "0700.HK",
        "text": "Tencent may rise!",
        "source": "Telegram"
    },
    {
        "ticker": "9988.HK",
        "text": "Alibaba looks promising!",
        "source": "LIHKG"
    }
]

for post in posts:
    print(post["text"])
    