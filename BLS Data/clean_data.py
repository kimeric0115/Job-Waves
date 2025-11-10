import json

input_file = "BLS Data/output/merged_data.json"
output_file = "BLS Data/output/cleaned_data.json"


with open(input_file, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

def create_unique_key(record):
    return (
        record.get("sector", "unknown"),
        record.get("year", "unknown"),
        record.get("month", "unknown"),
        record.get("content", "").strip() if record.get("content") else "",
        record.get("url", "").strip() if record.get("url") else ""
    )

seen = set()
unique_data = []

for record in raw_data:
    key = create_unique_key(record)
    if key not in seen:
        seen.add(key)
        unique_data.append(record)

print(f"Total data points: {len(unique_data)}")

with open(output_file, "w", encoding="utf-8") as f_out:
    json.dump(unique_data, f_out, indent=4)

print(f"Cleaned dataset saved as {output_file}")