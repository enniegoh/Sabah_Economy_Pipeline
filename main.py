# pipeline.py

import os
import re

import pandas as pd
import requests


# 1. define how to get the data through dosm api and bnm api
def fetch_data(api_id, state_filter = 'Sabah'):
    url = f"https://api.data.gov.my/data-catalogue?id={api_id}&filter={state_filter}@state"
    try:
        response = requests.get(url, timeout = 30)
        response.raise_for_status()
        return pd.DataFrame(response.json())
    except Exception as e:
        print(f"Failed to retrieve the data ({api_id}): {e}")
        return pd.DataFrame()  # return an empty dataframe


def fetch_bnm_interest_rate():
    """interest rate by month and year"""
    headers = {"Accept": "application/vnd.BNM.API.v1+json"}
    all_data = []

    # define the range of time
    years = [2025, 2026]
    months = list(range(1, 13))

    for year in years:
        for month in months:
            # 2026年只获取到8月
            if year == 2026 and month > 8:
                break

            url = f"https://api.bnm.gov.my/public/interest-rate/year/{year}/month/{month}"
            try:
                response = requests.get(url, headers = headers, timeout = 30)
                if response.status_code == 200:
                    data_json = response.json()
                    data_content = data_json.get('data')
                    if isinstance(data_content, list) and data_content:
                        for record in data_content:
                            record['request_year_month'] = f"{year}-{month:02d}"
                        all_data.extend(data_content)
                else:
                    print(f"Reason failed: {year}-{month:02d} (状态码: {response.status_code})")
            except Exception as e:
                print(f"Error ({year}-{month:02d}): {e}")

    return pd.DataFrame(all_data)


# 2. Clean the data for income and expenditure dataset
def clean_income_expenditure(df, col_name = 'parlimen'):
    if df.empty:
        return df
    # Remove the prefix at the parlimen column
    df['district'] = df[col_name].apply(lambda x: re.sub(r'P\.\d+\s', '', x))
    # Remove the parlimen column
    df.drop(columns = [col_name], inplace = True)
    # Convert the date to proper format and year and month
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
    return df


# same goes to cpi
def clean_cpi(df):
    if df.empty:
        return df
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
    return df


# same goes to crop production
def clean_crops(df):
    if df.empty:
        return df
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'])
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
    return df


# 3. merge the income and expenditure dataset
def merge_income_expenditure(df_income, df_expenditure):
    if df_income.empty or df_expenditure.empty:
        return pd.DataFrame()
    merged_df = pd.merge(
        df_income,
        df_expenditure,
        on = ['date', 'state', 'year', 'month', 'district'],
        how = 'inner'
    )
    return merged_df


# 4. Execute the pipeline
def run_pipeline():
    print("Start to run the pipeline...")

    # Create a "holder"
    os.makedirs('data', exist_ok = True)

    # 4.1 Retrieve the data
    print("Retrieving the data...")
    df_income_raw = fetch_data('hh_income_parlimen')
    df_expenditure_raw = fetch_data('hh_expenditure_parlimen')
    df_cpi_raw = fetch_data('cpi_state')
    df_crops_raw = fetch_data('crops_district_production')
    df_interest_raw = fetch_bnm_interest_rate()

    # 4.2 Data cleaning
    print("Data cleaning in progress...")
    df_income_clean = clean_income_expenditure(df_income_raw)
    df_expenditure_clean = clean_income_expenditure(df_expenditure_raw)
    df_cpi_clean = clean_cpi(df_cpi_raw)
    df_crops_clean = clean_crops(df_crops_raw)

    # 4.3 Merge
    print("Merging relevant data...")
    df_combined = merge_income_expenditure(df_income_clean, df_expenditure_clean)

    # 4.4 Compile the data in csv files
    print("Compiling CSV files...")
    df_combined.to_csv('data/sabah_income_expenditure.csv', index = False)
    df_cpi_clean.to_csv('data/sabah_cpi.csv', index = False)
    df_crops_clean.to_csv('data/sabah_crops.csv', index = False)
    df_interest_raw.to_csv('data/sabah_interest_rate.csv', index = False)

    print(f"The pipeline is completed and all the CSV files are stored in the 'data/' folder。")
    print(f"   - sabah_income_expenditure.csv ({len(df_combined)} rows)")
    print(f"   - sabah_cpi.csv ({len(df_cpi_clean)} rows)")
    print(f"   - sabah_crops.csv ({len(df_crops_clean)} rows)")
    print(f"   - sabah_interest_rate.csv ({len(df_interest_raw)} rows)")


# 5. Run the program
if __name__ == "__main__":
    run_pipeline()
