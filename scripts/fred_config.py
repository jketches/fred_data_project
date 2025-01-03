# fred config file

from fredapi import Fred
import pandas as pd

print("Fred class loaded:", Fred)


# Import the API key from config.py
from config import FRED_API_KEY


# Dictionary mapping FRED series codes to descriptive names
FRED_SERIES = {
    "DFF": "Federal Funds Effective Rate",
    "DGS3MO": "3-month Treasury Bill",
    "DGS1": "1-Year Treasury Yield",
    "DGS2": "2-Year Treasury Yield",
    "DGS5": "5-Year Treasury Yield",
    "DGS7": "7-Year Treasury Yield",
    "DGS10": "10-Year Treasury Yield",
}

# Function to fetch fred data using api key

def fetch_fred_data(series_ids, start_date=None, frequency=None):
    """
    Fetches data for specified FRED series IDs using the stored API key.
    
    Parameters:
        series_ids (list): A list of FRED series IDs to fetch.
        start_date (str): The start date for fetching data (format: "YYYY-MM-DD"). Default is None (all available data).
        frequency (str): Desired frequency for all series, e.g., "d" (daily), "m" (monthly). Default is None (native frequency).
        
    Returns:
        pd.DataFrame: A dataframe with each series as a column.
    """
    fred = Fred(api_key=FRED_API_KEY)
    data = pd.DataFrame()

    for series_id in series_ids:
        try:
            # Fetch series data
            series_data = fred.get_series(series_id, start=start_date)
            
            # Resample if frequency is specified
            if frequency:
                if frequency == "m":  # Monthly
                    series_data = series_data.resample("M").mean()
                elif frequency == "q":  # Quarterly
                    series_data = series_data.resample("Q").mean()
                elif frequency == "a":  # Annual
                    series_data = series_data.resample("A").mean()
                # Other frequencies can be added as needed
            
            data[series_id] = series_data
        except Exception as e:
            print(f"Error fetching series {series_id}: {e}")
    
    return data