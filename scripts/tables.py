import pandas as pd
import matplotlib.pyplot as plt

# Comparison table function
#*******************************

def create_comparison_table(data, series_list, custom_dates, title, output_file):
    """
    Create a comparison table showing the latest value of series and changes versus custom dates.
    
    Parameters:
        data (pd.DataFrame): A DataFrame containing the series data with a DatetimeIndex.
        series_list (list): List of series names (columns in the DataFrame) to include in the table.
        custom_dates (list): List of custom dates (strings or datetime objects) to compare against.
        title (str): Title for the table.
        output_file (str): Path to save the output table as an image.
    """
    # Ensure index is datetime
    if not isinstance(data.index, pd.DatetimeIndex):
        data.index = pd.to_datetime(data.index)
    
    # Convert custom_dates from strings to Timestamps
    custom_dates = [pd.Timestamp(date) for date in custom_dates]
    
    # Prepare the table data
    table_data = []
    headers = ["Series", "Current Value"] + [f"Chg. vs. {date.strftime('%m-%d')}" for date in custom_dates]
    
    for series in series_list:
        if series not in data.columns:
            print(f"Series {series} not found in data. Skipping.")
            continue
        
        # Get the last non-NA value and its date
        last_valid_index = data[series].last_valid_index()
        if last_valid_index is None:
            continue  # Skip if no valid data
        
        current_value = data[series].loc[last_valid_index]
        
        from fred_config import FRED_SERIES  # Import the friendly names dictionary
        friendly_name = FRED_SERIES.get(series, series)  # Default to series name if not in FRED_SERIES
        row = [friendly_name, f"{current_value:.2f}"]
        
        # Calculate changes vs. custom dates
        for custom_date in custom_dates:
            if custom_date in data.index:
                custom_value = data[series].loc[custom_date]
                if pd.notna(custom_value):
                    change = current_value - custom_value
                    row.append(f"{change:.2f}")
                else:
                    row.append("N/A")
            else:
                row.append("Date not found")
        
        table_data.append(row)
    
    # Create the figure and table
    fig, ax = plt.subplots(figsize=(8, 4))  # Adjust size to fit alongside charts in PDF
    ax.axis("off")
    
    # Add title
    ax.set_title(title, fontsize=14, fontweight="bold", pad=1)
    
    # Add the table
    table = ax.table(cellText=table_data, colLabels=headers, loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(headers))))  # Auto adjust column width
    
    # Save the table
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    #plt.show()
    plt.close()
    print(f"Table saved to {output_file}")

import pandas as pd
import matplotlib.pyplot as plt
from fred_config import FRED_SERIES


# Function for cumulative change table

def create_analysis_table(series, start_date, data, save_path):
    """
    Creates a table analyzing changes in series values starting from a specific date.

    Parameters:
        .
        series (str): series to analyze.
        start_date (str): Starting date for the analysis (format: "YYYY-MM-DD").
        data (pd.DataFrame): DataFrame containing the time series data.

    Returns:
        None: Displays the table in the notebook and saves it as an image.
    """
    # Ensure the start_date is a pandas timestamp
    start_date = pd.Timestamp(start_date)

    # Filter the data to include only rows after the starting date
    filtered_data = data.loc[start_date:]
    
    # Create the table data structure
    table_data = []

    # First column: Dates
    table_dates = filtered_data[series].dropna().index.strftime("%m-%d").tolist()

    table_data.append(["Date"] + table_dates)

    # Column values
    friendly_name = FRED_SERIES.get(series, series)
    series_data = filtered_data[series].dropna()

    # Calculate the starting value
    start_value = series_data.loc[start_date]

    # Calculate "Chg. vs. Starting Date"
    change_vs_start = series_data - start_value

    # Calculate "Daily Change"
    daily_change = series_data - series_data.ffill().shift(1)

    # Calculate "Daily Contribution to Total Change (%)"
    total_change = series_data.iloc[-1] - start_value
    daily_contribution = (daily_change / total_change) * 100

    # Add the columns to the table
    table_data.append(["Value"] + series_data.round(2).tolist())

    
    table_data.append(
        [f"Chg. vs. {start_date.strftime('%m-%d')}"]
        + change_vs_start.round(2).tolist()
    )
    table_data.append(
        [f"Daily Change"] + daily_change.round(2).tolist()
    )
    #table_data.append(
     #   [f"Daily Contribution (%)"]
     #   + daily_contribution.round(2).tolist()
    #)

    # Convert to DataFrame for visualization
    table_df = pd.DataFrame(table_data).transpose()

    # Plot the table
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.axis("off")
    table = ax.table(
        cellText=table_df.values,
        colLabels=None,
        cellLoc="center",
        loc="center",
    )
    table.auto_set_font_size(True)
    #table.set_fontsize(10)
    table.auto_set_column_width(col=list(range(len(table_df.columns))))

    
    # Add the title
    friendly_name = FRED_SERIES.get(series, series)
    plt.title(friendly_name, fontsize=14, weight="bold", pad=180)
    # Adjust layout to ensure title is at the top and the table fits nicely
    plt.subplots_adjust(top=0.75)  # Adjust the top margin to make space for the title

    ax.axis("off")

    # Save the table
    output_file = save_path
    plt.savefig(output_file, bbox_inches="tight", dpi=300)
    #plt.show()
    plt.close()
    print(f"Table saved to {output_file}")



