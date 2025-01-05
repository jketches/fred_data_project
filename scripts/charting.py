import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from fred_config import FRED_SERIES
import pandas as pd

def create_chart(data, series_list, start_date=None, title=None, show_data_label=False, 
                 vlines=None, show_table=False,custom_dates=None, save_path=None):
    """
    Creates a line chart for specified series with optional features like labels, vlines, and a data table.
    
    Parameters:
        data (pd.DataFrame): DataFrame containing the series as columns.
        series_list (list): List of column names in `data` to plot.
        start_date (str): The start date for filtering data (format: "YYYY-MM-DD").
        title (str): Title for the chart.
        show_data_label (bool): Whether to show a label for the last data point of each series.
        vlines (list): List of dates (strings in "YYYY-MM-DD" format) to mark with vertical lines. 
        show_table (bool): Whether to include a table of last dates and values below the chart.
        save_path (str): Path to save the chart as a PNG file.
    """
    # Filter the data by start_date
    if start_date:
        data = data.loc[start_date:]
    
    # Create the plot
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=6))  # Change '2' to adjust the spacing
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))  # Format labels as Year-Month
    # Adjust label density
    for series in series_list:
        ax.plot(data.index, data[series], label=FRED_SERIES.get(series, series))
        if show_data_label:
            # Add a label for the last data point
            last_date = data.index[-1]
            last_value = data[series].iloc[-1]
            ax.text(last_date, last_value, f"{last_value:.2f}", fontsize=8, ha="right")

    # Add vertical lines if specified
    if vlines:
        for vline in vlines:
            ax.axvline(pd.to_datetime(vline), color="black", linestyle="-", linewidth=0.8)
    
    # Set the title and legend
    ax.set_title(title if title else FRED_SERIES.get(series_list[0], series_list[0]))
    if len(series_list) > 1:
        ax.legend(loc="upper left", fontsize=8)

    # Add a table if specified
    if show_table:
        # Initialize table data
        #table_data = [["Date", "Value"]]
        # Add the last available data point
        # Get the last non-NaN value and corresponding date
        last_valid_index = data[series].last_valid_index()
        last_date = last_valid_index.strftime('%Y-%m-%d') if last_valid_index else 'No Data'
        last_value = data[series].loc[last_valid_index] if last_valid_index else 'N/A'
        
        # Build the table data
        table_data = [["Date","Value"]]+[[last_date, f"{last_value:.2f}" if pd.notna(last_value) else "N/A"]]
        # Add custom dates if provided
        if custom_dates:
            for date in custom_dates:
                if date in data[series].index:
                    value = data[series].loc[date]
                    table_data.append([date, f"{value:.2f}" if pd.notna(value) else "N/A"])
                else:
                    table_data.append([date, "N/A"])
        
        table = ax.table(cellText=table_data, cellLoc="center", colLabels=None,
                         loc="bottom", bbox=[0.1, -0.8, 0.8, 0.6])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)  # Adjust table size for better readability
    
    # Adjust layout
    plt.tight_layout()
    # Assuming 'ax' is your axes object
    ax.grid(axis='x', linestyle='--', color='gray', alpha=0.3)
    ax.grid(axis='y', linestyle='--', color='gray', alpha=0.3)

    # Save the plot
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        print(f"Chart saved to: {save_path}")
