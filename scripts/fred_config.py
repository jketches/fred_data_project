# fred config file
from fredapi import Fred
import pandas as pd
import time
import os
from pathlib import Path
import pickle
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
    "DAAA": "Moody's AAA Corporate Yield",
    "DBAA": "Moody's BAA Corporate Yield",
    "BAMLC0A1CAAAEY": "AAA Corporate Yield",
    "BAMLC0A2CAAEY": "AA Corporate Yield",
    "BAMLC0A3CAEY": "A Corporate Yield",
    "BAMLC0A4CBBBEY": "BBB Corporate Yield",
    "BAMLH0A1HYBBEY": "BB Corporate Yield",
    "BAMLH0A2HYBEY": "B Corporate Yield",
    "BAMLH0A3HYCEY": "CCC and lower Corporate Yield",
    "BAMLC0A1CAAA": "AAA Corporate Spread",
    "BAMLC0A2CAA": "AA Corporate Spread",
    "BAMLC0A3CA": "A Corporate Spread",
    "BAMLC0A4CBBB": "BBB Corporate Spread",
    "BAMLH0A1HYBB": "BB Corporate Spread",
    "BAMLH0A2HYB": "B Corporate Spread",
    "BAMLH0A3HYC": "CCC and lower Corporate Spread"
}

def get_cache_filename(series_ids, start_date, frequency, results_dir):
    """Generate a unique filename for the cached data based on parameters"""
    series_hash = '_'.join(sorted(series_ids))  # Sort to ensure consistent naming
    params = f"{series_hash}_{start_date or 'all'}_{frequency or 'native'}"
    # You can choose between csv or pickle format
    return Path(results_dir) / f"fred_data_{params}.csv"  # or .pkl for pickle

def fetch_fred_data(series_ids, start_date=None, frequency=None, results_dir="results", 
                   use_cache=True, force_refresh=False, save_format='csv'):
    """
    Fetches data for specified FRED series IDs using the stored API key.
    
    Parameters:
        series_ids (list): A list of FRED series IDs to fetch.
        start_date (str): The start date for fetching data (format: "YYYY-MM-DD"). Default is None (all available data).
        frequency (str): Desired frequency for all series, e.g., "d" (daily), "m" (monthly). Default is None (native frequency).
        results_dir (str): Directory to save the downloaded data.
        use_cache (bool): Whether to use cached data if available.
        force_refresh (bool): Whether to force new download even if cache exists.
        save_format (str): Format to save data ('csv' or 'pickle')
        
    Returns:
        pd.DataFrame: A dataframe with each series as a column.
    """
    # Create results directory if it doesn't exist
    results_dir = Path(results_dir)
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate cache filename based on save format
    if save_format == 'pickle':
        cache_file = results_dir / f"{get_cache_filename(series_ids, start_date, frequency, results_dir).stem}.pkl"
    else:  # default to csv
        cache_file = get_cache_filename(series_ids, start_date, frequency, results_dir)
    
    # Check cache if enabled
    if use_cache and not force_refresh and cache_file.exists():
        print(f"Loading cached data from {cache_file}")
        try:
            if save_format == 'pickle':
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
            else:  # csv
                return pd.read_csv(cache_file, index_col=0, parse_dates=True)
        except Exception as e:
            print(f"Error reading cache file: {e}")
            print("Proceeding with fresh download...")
    
    start_time = time.time()
    print(f"Starting download of {len(series_ids)} series...")
    
    fred = Fred(api_key=FRED_API_KEY)
    data = pd.DataFrame()
    completed = 0
    
    for series_id in series_ids:
        try:
            # Fetch series data with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    series_data = fred.get_series(series_id, start=start_date)
                    break
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    print(f"Retry {attempt + 1} for {series_id}")
                    time.sleep(1)  # Wait before retry
            
            # Resample if frequency is specified
            if frequency:
                if frequency == "m":  # Monthly
                    series_data = series_data.resample("M").mean()
                elif frequency == "q":  # Quarterly
                    series_data = series_data.resample("Q").mean()
                elif frequency == "a":  # Annual
                    series_data = series_data.resample("A").mean()
            
            data[series_id] = series_data
            completed += 1
            print(f"Completed {completed}/{len(series_ids)}: {series_id}")
            
        except Exception as e:
            print(f"Error fetching series {series_id}: {e}")
    
    elapsed = time.time() - start_time
    print(f"Download completed in {elapsed:.2f} seconds")
    print(f"Successfully downloaded {len(data.columns)} out of {len(series_ids)} series")
    
    # Save to cache if we have data
    if not data.empty:
        try:
            if save_format == 'pickle':
                with open(cache_file, 'wb') as f:
                    pickle.dump(data, f)
            else:  # csv
                data.to_csv(cache_file)
            print(f"Data saved to {cache_file}")
        except Exception as e:
            print(f"Error saving cache file: {e}")
    
    return data