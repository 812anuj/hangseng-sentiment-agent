
from transformers import pipeline

# Name of our financial sentiment model
MODEL_NAME = "Kenpache/finbert-multilingual-v2"

print("Loading financial sentiment model...")

# Load the pretrained model
classifier = pipeline(
    "text-classification",
    model=MODEL_NAME,
    device=-1
)

print("Model loaded successfully!")

# Two sample financial news headlines
headlines = [
    "The company reported record profits and strong revenue growth.",
    "The company reported a sharp decline in profits and revenue."
]

# Predict sentiment

# Test all three sentiment probabilities
result = classifier(
    "The company reported strong profits and revenue growth.",
    top_k=None
)

print("\nAll sentiment probabilities:")

for prediction in result:
    print(
        prediction["label"],
        ":",
        round(prediction["score"], 4)
    )

