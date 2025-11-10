import json
import pandas as pd
from datetime import datetime

file1 = "BLS Data/reddit/reddit_post_grad_data_2018_2020_final.json"
file2 = "BLS Data/reddit/reddit_post_grad_data_2021_2023_final.json"
output_file = "BLS Data/output/reddit_post_grad_data_merged.json"

# Load both JSON files
with open(file1, "r", encoding="utf-8") as f1, open(file2, "r", encoding="utf-8") as f2:
    data1 = json.load(f1)
    data2 = json.load(f2)

# Merge the data (assuming both files contain lists)
merged_data = data1 + data2  # Concatenating lists

# Save the merged JSON
with open(output_file, "w", encoding="utf-8") as f_out:
    json.dump(merged_data, f_out, indent=4)

bls_file = "BLS Data/output/final_output.json"
reddit_file = output_file

# Load data
with open(bls_file, "r") as f:
    bls_data = json.load(f)
bls_df = pd.DataFrame(bls_data)

with open(reddit_file, "r") as f:
    reddit_data = json.load(f)
reddit_df = pd.DataFrame(reddit_data)

# Convert Reddit timestamp to year and month
reddit_df["timestamp"] = pd.to_datetime(reddit_df["timestamp"])
reddit_df["year"] = reddit_df["timestamp"].dt.year.astype(str)
reddit_df["month"] = reddit_df["timestamp"].dt.strftime("%B") 

# Rename BLS columns for consistency
bls_df = bls_df.rename(columns={"name": "sector", "period_name": "month"})
bls_df["year"] = bls_df["year"].astype(str)

# Ensure only matching years are used in merging
valid_years = set(bls_df["year"]) & set(reddit_df["year"])
reddit_df = reddit_df[reddit_df["year"].isin(valid_years)]

merged_df = bls_df.merge(
    reddit_df,  
    on=["sector", "year", "month"],
    how="left"
)

merged_df = merged_df.drop(columns=["timestamp", "period"], errors="ignore")  # Remove timestamp & period

merged_file = "BLS Data/output/merged_data.json"
merged_df.to_json(merged_file, orient="records", indent=4)