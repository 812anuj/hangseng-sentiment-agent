
import json

# Open the cleaned JSON file
with open(
    "data/processed/lihkg_cleaned.json",
    "r",
    encoding="utf-8"
) as file:

    cleaned_data = json.load(file)


# Verify the data
print("Total cleaned records:", len(cleaned_data))

print("First record ID:", cleaned_data[0]["post_id"])

print("First record source:", cleaned_data[0]["source"])

print("First record exchange:", cleaned_data[0]["exchange"])

print("First record text:", cleaned_data[0]["text"])
