import json
import os

# Input and output file paths
text_file_paths = [r"BLS Data\industry_inputs\CE_inputs.txt", r"BLS Data\industry_inputs\JT_inputs.txt", r"BLS Data\industry_inputs\SMU_inputs.txt"]
json_file_paths = ["CE_outputs.json", "JT_outputs.json", "SMU_outputs.json"]  # Fixed file extensions

# Create output directory if it doesn't exist
os.makedirs("BLS Data\outputs", exist_ok=True)

# Process each text file
for i in range(len(text_file_paths)):
    text_file = text_file_paths[i]
    json_file = json_file_paths[i]

    # Read tab-separated TXT file
    with open(text_file, "r") as file:
        lines = file.readlines()

    # Extract headers from the first row
    headers = lines[0].strip().split("\t")

    # Convert each row to a dictionary
    data_list = []
    for line in lines[1:]:  # Skip header
        values = line.strip().split("\t")
        data_list.append(dict(zip(headers, values)))

    # Save to JSON file
    json_output_path = f"BLS Data/outputs/{json_file}"
    with open(json_output_path, "w") as json_out:
        json.dump(data_list, json_out, indent=4)

    print(f"JSON file saved: {json_file}")