import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.dates import DateFormatter

# Import FRED config for variable names
from fred_config import FRED_SERIES

def create_chart(data, variables, start_date=None, end_date=None, title=None, 
                 show_data_label=False, vlines=None, show_table=False, save_path=None):
    """
    Generates a line chart for single variables or groups of variables.

    Parameters:
        data (pd.DataFrame): The data containing the variables as columns.
        variables (list): List of variables to plot (single or grouped).
        start_date (str): Start date for the chart (format: "YYYY-MM-DD").
        end_date (str): End date for the chart (format: "YYYY-MM-DD").
        title (str): Title of the chart (None for single variable charts).
        show_data_label (bool): Whether to show data labels for the last data point.
        vlines (list): Dates for vertical lines (format: "YYYY-MM-DD").
        show_table (bool): Whether to show a table of last values in the chart.
        save_path (str): File path to save the chart (e.g., "results/chart.png").
    
    Returns:
        None
    """
    # Filter data by date range
    if start_date:
        data = data[data.index >= start_date]
    if end_date:
        data = data[data.index <= end_date]

    # Initialize the figure
    fig, ax = plt.subplots(figsize=(5, 4))  # Suitable for PDF grid (2x3 charts per page)

    # Plot the variables
    for var in variables:
        if var in data.columns:
            ax.plot(data.index, data[var], label=FRED_SERIES.get(var, var))

    # Title and legend
    if len(variables) == 1:
        # Single variable: use its name as the title, no legend
        ax.set_title(FRED_SERIES.get(variables[0], variables[0]), fontsize=12)
    else:
        # Group of variables: use the provided title and a legend
        ax.set_title(title if title else "Chart", fontsize=12)
        ax.legend(fontsize=9)

    # Add vertical lines
    if vlines:
        for vline in vlines:
            ax.axvline(pd.to_datetime(vline), color="red", linestyle="--", linewidth=1)

    # Add data labels for the last data point
    if show_data_label:
        for var in variables:
            if var in data.columns:
                last_date = data[var].last_valid_index()
                last_value = data[var].loc[last_date]
                ax.text(last_date, last_value, f"{last_value:.2f}", fontsize=8, color="black")

    # Table of last data values
    if show_table:
        last_values = {
            var: [data[var].last_valid_index().strftime("%Y-%m-%d"), f"{data[var].iloc[-1]:.2f}"]
            for var in variables if var in data.columns
        }
        cell_text = [v for v in last_values.values()]
        row_labels = [FRED_SERIES.get(var, var) for var in variables if var in data.columns]
        col_labels = ["Last Date", "Value"]
        table = ax.table(cellText=cell_text, rowLabels=row_labels, colLabels=col_labels,
                         loc="bottom", bbox=[0, -0.4, 1, 0.2])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.2)

    # Formatting
    ax.xaxis.set_major_formatter(DateFormatter("%Y-%m"))
    ax.set_ylabel("Value")
    ax.grid(True, linestyle="--", alpha=0.5)

    # Tight layout and save
    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
    plt.show()
