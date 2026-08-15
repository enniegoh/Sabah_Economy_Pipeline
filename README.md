# Sabah Economic Data Pipeline

An automated ETL pipeline that fetches, cleans, and merges Sabah's key economic indicators from the official OpenDOSM API.

## Data Sources
- **Household Income & Expenditure** (by Parliament)
- **Consumer Price Index (CPI)** (by State)
- **Crop Production** (by District)

## How It Works
1. Fetches data from `api.data.gov.my` using Python `requests`.
2. Cleans and transforms data with `pandas` (handles date formatting, extracts district names).
3. Merges income and expenditure datasets into a single table.
4. Saves the final datasets as CSV files ready for analysis in Power BI.

## Automation
This pipeline is designed to run daily via **GitHub Actions**, ensuring that the data is always up-to-date without manual intervention.

## Output Files
- `sabah_income_expenditure.csv`
- `sabah_cpi.csv`
- `sabah_crops.csv`

## Libraries And Software Used
- Python (requests, pandas)
- GitHub Actions (CI/CD)
- OpenDOSM API
