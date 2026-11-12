
def normalize_post(raw_post, source, ticker, company, exchange):

    post = {

        # Post identification
        "post_id": (
            raw_post.get("id")
            or raw_post.get("thread_id")
            or raw_post.get("messageId")
        ),

        # Stock information
        "ticker": ticker,
        "company": company,
        "exchange": exchange,

        # Platform information
        "source": source,

        # Post content
        "text": (
            raw_post.get("message")
            or raw_post.get("content")
            or raw_post.get("text")
            or ""
        ),

        # Engagement
        "likes": raw_post.get(
            "like_count",
            raw_post.get("likes", 0)
        ),

        "comments": raw_post.get(
            "reply_count",
            raw_post.get("comment_count", 0)
        ),

        "shares": raw_post.get(
            "shares",
            raw_post.get("forwards", 0)
        ),

        # Author information
        "author": raw_post.get(
            "author",
            raw_post.get("authorName")
        ),

        "author_followers": raw_post.get(
            "author_followers"
        ),

        # Date and link
        "timestamp_utc": (
            raw_post.get("created_at")
            or raw_post.get("publishedAt")
            or raw_post.get("timestamp")
        ),

        "url": (
            raw_post.get("thread_url")
            or raw_post.get("messageUrl")
            or raw_post.get("url")
        )
    }

    return post


# Simulated LIHKG data
lihkg_post = {
    "thread_id": "123456",
    "content": "Tencent business looks promising!",
    "author": "Investor123",
    "like_count": 50,
    "reply_count": 12,
    "created_at": "2026-11-09T08:30:00Z",
    "thread_url": "https://lihkg.com/"
}


# Normalize the LIHKG post
clean_post = normalize_post(
    raw_post=lihkg_post,
    source="LIHKG",
    ticker="0700.HK",
    company="Tencent",
    exchange="Hong Kong"
)


print("Normalized LIHKG post:")

for key, value in clean_post.items():
    print(f"{key}: {value}")
