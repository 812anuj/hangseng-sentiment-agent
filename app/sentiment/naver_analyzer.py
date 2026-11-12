import json
from pathlib import Path
from transformers import pipeline

INPUT_PATH = Path("data/processed/naver_cleaned.json")
OUTPUT_PATH = Path("data/processed/naver_sentiment.json")

MODEL_NAME = "snunlp/KR-FinBert-SC"

print("Loading Korean financial sentiment model...")

analyzer = pipeline(
    "text-classification",
    model=MODEL_NAME,
    tokenizer=MODEL_NAME
)

def normalize_label(label):
    label = label.lower()

    if "negative" in label or "부정" in label:
        return "negative"

    if "positive" in label or "긍정" in label:
        return "positive"

    if "neutral" in label or "중립" in label:
        return "neutral"

    # Fallback for models returning LABEL_0, LABEL_1, etc.
    label_map = {
        "label_0": "negative",
        "label_1": "neutral",
        "label_2": "positive"
    }

    return label_map.get(label, "neutral")


def analyze_posts():
    with INPUT_PATH.open("r", encoding="utf-8") as file:
        posts = json.load(file)

    results = []

    for index, post in enumerate(posts, start=1):
        text = f"{post['title']} {post['text']}".strip()

        if not text:
            continue

        prediction = analyzer(
            text,
            truncation=True,
            max_length=512
        )[0]

        sentiment = normalize_label(prediction["label"])
        confidence = float(prediction["score"])

        if sentiment == "positive":
            sentiment_score = confidence
        elif sentiment == "negative":
            sentiment_score = -confidence
        else:
            sentiment_score = 0.0

        post["sentiment"] = sentiment
        post["sentiment_confidence"] = round(confidence, 4)
        post["sentiment_score"] = round(sentiment_score, 4)

        results.append(post)

        if index % 10 == 0:
            print(f"Analyzed {index}/{len(posts)} posts")

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(results, file, ensure_ascii=False, indent=4)

    print("\nNaver sentiment analysis completed!")
    print("Total analyzed:", len(results))
    print("Saved to:", OUTPUT_PATH)

    if results:
        print("\nFirst analyzed post:")
        print(json.dumps(results[0], ensure_ascii=False, indent=4))


if __name__ == "__main__":
    analyze_posts()