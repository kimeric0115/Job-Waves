import json
import pandas as pd
import xgboost
import numpy as np
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
import matplotlib.pyplot as plt
import seaborn as sns

input_file = '../data_deliverable/BLS_Reddit Merged/cleaned_data.json'
# data_file = "hypo2_data.json"

with open(input_file, "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.read_json(input_file)

months = {"January": 1,
          "February": 2,
          "March": 3,
          "April": 4,
          "May": 5,
          "June": 6,
          "July": 7,
          "August": 8,
          "September": 9,
          "October": 10,
          "November": 11,
          "December": 12}

# -----------------------------------------------------------------------
# Data Cleaning Stage

# After reading in the JSON file, we clean the data by removing Reddit posts and getting rid of duplicates from our data deliverable stage
dropped_labels = ["subreddit", "type", "content", "upvotes", "url", "comments"]
df = df.drop(columns=dropped_labels).drop_duplicates(keep='first')


# Add a time index for the model
df['month'] = df["month"].map(months)
df['date'] = pd.to_datetime(df[['year', 'month']].assign(day=1))

# Sort before assigning index
df = df.sort_values(['sector', 'date'])

# Generate time index **within each industry**
df['time_index'] = df.groupby('sector')['date'].rank(method='dense').astype(int) - 1

df = df.drop(labels='date', axis=1)

df.sort_values(by=['sector', 'time_index'])

df.rename(columns={'Number of Job Openings':'num_job_openings',
                   'Average Earnings of all employees (hourly)':'avg_earnings',
                   'All employees (thousands)':'all_employees'},inplace=True)

# print(df.head(10))
# print(df.tail(10))

# -----------------------------------------------------------------------
# Model Creation Stage

rmse_dict = {}
rmse_arr = []
rmse_train_arr = []
rmse_baseline_arr = []
df['sector'] = df['sector'].str.strip()  # remove extra spaces
sectors = df['sector'].unique()

feature_dict = {}

for sector in sectors:
    temp = df[df['sector'] == sector].copy()
    temp = temp.drop(labels=['sector', 'year', 'month'], axis=1)

    temp = temp.sort_values('time_index')

    # Creating a shift to illustrate a trend between time t and t-2
    temp['Job Openings'] = temp['num_job_openings'].shift(2)
    temp['Average Earnings'] = temp['avg_earnings'].shift(2)
    temp['Employee Count'] = temp['all_employees'].shift(2)
    
    y = temp['num_job_openings']

    # Getting rid of null values
    temp = temp.dropna(subset=['num_job_openings', 'avg_earnings', 'all_employees'], how='all')

    if temp['Average Earnings'].isna().sum() > 0:
        X = temp[['Job Openings','Employee Count']]
    elif temp['Employee Count'].isna().sum() > 0:
        X = temp[['Job Openings','Average Earnings']]
    else:
        X = temp[['Job Openings','Average Earnings','Employee Count']]


    # Using k-fold cross-validation across a temporal train-test split
    tscv = TimeSeriesSplit(n_splits = 5)
    nrmse = []
    nrmse_train = []
    nrmse_baseline = []

    feature_importances = []

    for train_index,test_index in tscv.split(X):
        X_train, y_train = X.iloc[train_index], y.iloc[train_index]
        X_test, y_test = X.iloc[test_index], y.iloc[test_index]

        model = XGBRegressor()
        model.fit(X_train, y_train)

        preds = model.predict(X_test)
        preds_train = model.predict(X_train)

        rmse = np.sqrt(mean_squared_error(y_test,preds, squared=False))
        nrmse.append(rmse / np.mean(y_test))

        rmse_train = np.sqrt(mean_squared_error(y_train, preds_train, squared=False))
        nrmse_train.append(rmse_train / np.mean(y_train))

        # Lagged predictor baseline: predict using t-2 lag to match XGBoost
        y_shifted = y.shift(2)
        y_test_lagged = y_shifted.iloc[test_index]
        y_test_lagged = y_test_lagged.fillna(method='bfill')  # or .fillna(0)

        lagged_preds = y_test_lagged.values  # convert to numpy array

        rmse_baseline = np.sqrt(mean_squared_error(y_test, lagged_preds, squared=False))
        nrmse_baseline.append(rmse_baseline / np.mean(y_test))


        # Getting importance values for the Model
        booster = model.get_booster()
        importance = booster.get_score(importance_type='gain')
        feature_importances.append(importance)
    
    # Normalizing the Root-mean-squared error (RMSE) to make the errors comparable regardless of data set
    # Taking the mean of of all k-folds to get a single normalized RMSE value for a single industry
    nrmse = np.mean(np.array(nrmse))
    nrmse_train = np.mean(np.array(nrmse_train))
    nrmse_baseline = np.mean(np.array(nrmse_baseline))

    # Getting importance scores aggregated across K-folds via mean
    importance_df = pd.DataFrame(feature_importances).fillna(0)
    feature_dict[sector] = importance_df
    mean_importance = importance_df.mean(axis=0).sort_values(ascending=False)

    rmse_dict[sector] = {"NRMSE": nrmse,
                         "Baseline NRMSE": nrmse_baseline,
                         "Error Reduction": nrmse_baseline-nrmse,
                         "Mean Importance Score": mean_importance} # dictionary of each industry's loss

    rmse_arr.append(nrmse)
    rmse_train_arr.append(nrmse_train)
    rmse_baseline_arr.append(nrmse_baseline)


rmse_arr = np.array(rmse_arr)
rmse_train_arr = np.array(rmse_train_arr)
rmse_baseline_arr = np.array(rmse_baseline_arr)

#-------------------------------------------------------------------------
# Printing results


print(f"Average Normalized Training RMSE across sectors: {np.mean(rmse_train_arr):.5f}")
print(f"Average Normalized Testing RMSE across sectors: {np.mean(rmse_arr):.5f}")
print(f"Variance of Normalized RMSE: {np.var(rmse_arr):.5f}")
print(f"Average Error Reduction from Baseline: {np.mean(rmse_baseline_arr-rmse_arr):.5f}")

# Sector-wise breakdown
df_rmse = pd.DataFrame([
    {
        "Sector": sector,
        "NRMSE": vals["NRMSE"],
        "Baseline NRMSE": vals["Baseline NRMSE"],
        "Error Reduction": vals["Error Reduction"],
        "Mean Importance Score": vals["Mean Importance Score"]
    }
    for sector, vals in rmse_dict.items()
])
# print(f"\nSector-wise Error Reductions:")
# print(df_rmse[['Sector', 'Error Reduction']].to_string(index=False))

# print("\nSector-wise Mean Importance Scores:")
# for sector, vals in rmse_dict.items():
#     print(f"\nSector: {sector}")
#     for feat, score in vals["Mean Importance Score"].items():
#         print(f"  {feat}: {score:.5f}")


#----------------------------------------------------------------------------
# Visualizations

import os

main_folder = 'visualizations'
subfolder = os.path.join(main_folder, 'hypo2_plots')
os.makedirs(subfolder, exist_ok=True)


# Set seaborn colorblind theme
sns.set_theme(style='whitegrid', palette='colorblind')

# Graph 1: Histogram
plt.figure(figsize=(8, 6))
sns.histplot(df_rmse['NRMSE'], bins=10, kde=True, color='tab:blue')
plt.xlabel('Normalized RMSE')
plt.title('Distribution of Predictive Error Across Sectors')
plt.tight_layout()
plt.savefig(os.path.join(subfolder, 'histogram_nrmse.png'))
plt.close()

# Graph 2: Bar Plot (side-by-side)
abbrev_map = {
    'private education and health services': 'Edu/Health',
    'professional and business services': 'Prof/Business',
    'trade, transportation, and utilities': 'Trade/Transport',
    'leisure and hospitality': 'Leisure',
    'financial activities': 'Finance',
    'mining and logging': 'Mining',
    'manufacturing': 'Manufacturing',
    'government': 'Govt',
    'construction': 'Construction',
    'information': 'Info'
}

df_rmse_sorted = df_rmse.sort_values(by='NRMSE')
df_rmse_sorted['Sector'] = df_rmse_sorted['Sector'].replace(abbrev_map)
x = np.arange(len(df_rmse_sorted['Sector']))
width = 0.35

plt.figure(figsize=(14, 6))
plt.bar(x - width/2, df_rmse_sorted['NRMSE'], width, label='XGBoost NRMSE', color='tab:blue')
plt.bar(x + width/2, df_rmse_sorted['Baseline NRMSE'], width, label='Baseline NRMSE', color='tab:orange')

plt.ylabel('Normalized RMSE')
plt.title('XGBoost vs. Baseline NRMSE by Sector')
plt.xticks(x, df_rmse_sorted['Sector'], rotation=45, ha='right', fontsize=10)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(subfolder, 'barplot_nrmse_comparison.png'))
plt.close()

# Graph 3: Line chart (feature importance over folds)
all_importances_list = []
for sector, df_sector in feature_dict.items():
    df_sector = df_sector.copy()
    df_sector['Sector'] = sector
    df_sector['Fold'] = range(len(df_sector))
    all_importances_list.append(df_sector)

all_importances = pd.concat(all_importances_list, ignore_index=True)
feature_columns = [col for col in all_importances.columns if col not in ['Sector', 'Fold']]

# Use seaborn color palette (colorblind-safe)
colors = sns.color_palette('colorblind', n_colors=len(all_importances['Sector'].unique()))

for feature in feature_columns:
    plt.figure(figsize=(12, 6))
    for idx, sector in enumerate(all_importances['Sector'].unique()):
        sector_data = all_importances[all_importances['Sector'] == sector]
        plt.plot(
            sector_data['Fold'],
            sector_data[feature],
            label=sector,
            marker='o',
            color=colors[idx % len(colors)]
        )
    plt.xlabel('Fold Number', fontsize=12)
    plt.ylabel('Gain Importance', fontsize=12)
    plt.title(f'{feature} Importance over Time Across Sectors', fontsize=14)
    plt.legend(loc='upper left', fontsize=8)
    plt.xticks(fontsize=10)
    plt.yticks(fontsize=10)
    plt.tight_layout()
    plt.savefig(os.path.join(subfolder, f'lineplot_{feature}_importance.png'))
    plt.close()