# Employment & Unemployment (CE): Average Hourly Earnings of All Employees, In Dollars
# Job Openings and Labor Turnover Survey (JT): All employees, in thousands
# State and Area Employment, Hours, and Earnings (SMU): measuring the number of job openings in a given period of time

import json
import pandas as pd
from getting_data import run

dict = run()

files = [
    r"final-projects-students-postgrad\BLS Data\output\CE_data.json",
    r"final-projects-students-postgrad\BLS Data\output\JT_data.json",
    r"final-projects-students-postgrad\BLS Data\output\SMU_data.json"
]
values = ["Average Earnings of all employees (hourly)", "Number of Job Openings", "All employees (thousands)"]

df = []
for file, value in zip(files, values):
    with open(file, "r") as file:
        json_data = json.load(file)
    series_list = json_data["Results"]["series"]

    flat_data = []
    for series in series_list:
        series_id = series["seriesID"]
        # got rid of series id for now in the actual dataframe

        for entry in series["data"]:
            flat_data.append({
                "name": dict[series_id],
                "year": entry["year"],
                "period": entry["period"],
                "period_name": entry["periodName"],
                value: float(entry["value"]),  # Convert to numerical format
            })
    df.append(pd.DataFrame(flat_data))

df_ce, df_jt, df_smu = df[0], df[1], df[2]


# taking care of the case where df_jt has "federal" and "state and local" rather than just "government" like the other datasets
df_jt["name"] = df_jt["name"].replace({"federal": "government", "state and local": "government"})

df_jt_agg = df_jt.groupby(["name", "year", "period", "period_name"], as_index=False).agg({"Number of Job Openings": "sum"})

# the final data frame merging all the datasets
df_final = df_jt_agg.merge(df_ce, on=["name","year","period","period_name"],how = "left").merge(df_smu, on = ["name","year","period","period_name"], how = "left")
df_final = df_final[df_final['name'] != "other services"]
df_final.to_json(r"final-projects-students-postgrad\BLS Data\output\final_output.json",orient = "records", indent= 4)