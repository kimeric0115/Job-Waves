import requests
import json
import os

# CE = Employment & Unemployment: Average Hourly Earnings of All Employees, In Dollars
# JT = State and Area Employment, Hours, and Earnings: measuring the number of job openings in a given period of time
# SMU = Job Openings and Labor Turnover Survey: All employees, in thousands


def run():
    industry_file_paths = [
    r"final-projects-students-postgrad\BLS Data\industry_inputs\CE_outputs.json",
    r"final-projects-students-postgrad\BLS Data\industry_inputs\JT_outputs.json",
    r"final-projects-students-postgrad\BLS Data\industry_inputs\SMU_outputs.json"
]

    # Define API headers
    headers = {'Content-type': 'application/json'}

    # Unloading the JSON files into variables
    files = []
    for file in industry_file_paths:
        with open(file, "r") as json_file:
            files.append(json.load(json_file))

    # Finding the list of industries that fall into display_level 2
    arr1, arr2, arr3 = [], [], []
    filtered_files = [[],[],[]]
    for i in range(2):
        for row in files[i]:
            if row["display_level"] == "2":
                if "industry_name" in row.keys():
                    filtered_files[0].append(row)
                    arr1.append(row["industry_name"].lower())
                else:
                    filtered_files[1].append(row)
                    arr2.append(row["industry_text"].lower())
    for row in files[2]:
        if row["industry_name"].lower() in arr1 or row["industry_name"].lower() in arr2:
            filtered_files[2].append(row)
            arr3.append(row["industry_name"])

    series_id = [[],[],[]]
    dict = {}
    for i in range(len(filtered_files)):
        for row in filtered_files[i]:
            if i == 0:
                code = f"CEU{row['industry_code']}03"
                dict[code] = row["industry_name"].lower()
                series_id[i].append(code)
            elif i == 1:
                code = f"JTU{row['industry_code']}000000000JOL"
                dict[code] = row["industry_text"].lower()
                series_id[i].append(code)
            else:
                code = f"SMU1919780{row['industry_code']}01"
                dict[code] = row["industry_name"].lower()
                series_id[i].append(f"SMU1919780{row['industry_code']}01")
    # print(dict)

    data = []
    for series in series_id:
        data.append(json.dumps({
            "seriesid": series,
            "startyear": "2018",
            "endyear": "2023"
        }))

    # Send request to BLS API
    i=0
    file_names = ["CE","JT", "SMU"]
    for datum in data:
        p = requests.post('https://api.bls.gov/publicAPI/v1/timeseries/data/', data=datum, headers=headers)

        # Check API response
        if p.status_code != 200:
            print(f"Error: API request failed with status code {p.status_code}")
            exit()

        # Parse API response
        json_data = json.loads(p.text)

        # Create output directory if it doesn't exist
        os.makedirs("./output", exist_ok=True)

        # Save full API response to JSON
        json_output_path = f"C:/Users/user/Documents/Data Science Final Project/final-projects-students-postgrad/BLS Data/output/{file_names[i]}_data.json"
        i+=1
        with open(json_output_path, "w") as json_file:
            json.dump(json_data, json_file, indent=4)

        print(f"Full JSON response saved: {json_output_path}")
    
    return dict