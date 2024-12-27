import os
from datetime import datetime
from sklearn.linear_model import LinearRegression
import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk
import threading
from yahoo_fin import options

############################################################################################################
# Option-Selling Strategy for ETFs
#
# ONLY FOR EDUCATIONAL PURPOSES
############################################################################################################


def detect_trends(data):
    """
    Identifies upward and downward trendlines based on highs and lows.
    """
    close_prices = data['Close']
    local_maxima_indices = argrelextrema(close_prices.values, np.greater, order=5)[0]
    local_minima_indices = argrelextrema(close_prices.values, np.less, order=5)[0]

    maxima_points = data.iloc[local_maxima_indices].reset_index()
    minima_points = data.iloc[local_minima_indices].reset_index()

    return maxima_points, minima_points

def clean_data(series):
    """
    Cleans the data to ensure it contains only numeric values.
    """
    if isinstance(series, pd.DataFrame):
        series = series.squeeze()
    elif isinstance(series, np.ndarray) and series.ndim > 1:
        series = pd.Series(series.ravel())
    return pd.to_numeric(series, errors='coerce').dropna()

def get_iv(symbol):
    """
    Fetches the implied volatility (IV) from Yahoo Finance's options chain.
    """
    try:
        calls = options.get_calls(symbol)
        iv_values = calls['Implied Volatility'].dropna().str.rstrip('%').astype(float) / 100
        average_iv = iv_values.mean()
        return average_iv
    except Exception as e:
        print(f"Error fetching IV for {symbol}: {e}")
        return None

def calculate_rsi(data, window=14):
    """
    Calculates the Relative Strength Index (RSI).
    """
    delta = data['Close'].diff(1)
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(window=window).mean()
    avg_loss = loss.rolling(window=window).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    return data

def calculate_trendline(data):
    """
    Calculates the trendline based on closing prices.
    """
    data = data.reset_index()
    x = np.arange(len(data)).reshape(-1, 1)
    y = data['Close'].values

    model = LinearRegression()
    model.fit(x, y)
    trendline = model.predict(x)
    slope = float(model.coef_[0])
    return trendline, slope

def calculate_bollinger_bands(data, window=20, num_std_dev=2):
    """
    Calculates Bollinger Bands based on closing prices.
    """
    rolling_mean = data['Close'].rolling(window=window).mean()
    rolling_std = data['Close'].rolling(window=window).std()

    upper_band = rolling_mean + num_std_dev * rolling_std
    lower_band = rolling_mean - num_std_dev * rolling_std

    return rolling_mean, upper_band, lower_band

def backtest_strategy(data, strike_price, dte):
    """
    Backtests a put-option strategy.
    """
    profits = []
    close_prices = data['Close'].values

    for i in range(len(close_prices) - dte):
        option_start_price = close_prices[i]
        option_end_price = close_prices[i + dte]

        if float(option_end_price) >= float(strike_price):
            profit = option_start_price * 0.02
        else:
            profit = strike_price - option_end_price

        profits.append(profit)

    total_profit = np.sum(profits)
    avg_profit = np.mean(profits) if profits else 0

    return total_profit, avg_profit

def generate_put_recommendation(data, support_levels, moving_average_200, iv):
    """
    Generates a put recommendation based on support levels and IV.
    """
    if support_levels.empty:
        return "No support levels found. Recommendation not possible."

    current_price = float(data['Close'].iloc[-1])
    nearest_support = min(support_levels, key=lambda x: abs(current_price - x))
    strike_price = round(nearest_support * 0.95, 2)
    dte = 45

    recommendation = (
        f"Current Price: {current_price:.2f} USD\n"
        f"Nearest Support: {nearest_support:.2f} USD\n"
        f"200-Day Average: {moving_average_200:.2f} USD\n"
        f"Recommended Strike Price: {strike_price:.2f} USD\n"
        f"Recommended Duration (DTE): {dte} days\n"
        f"Implied Volatility (IV): {iv:.2%}\n"
        "Comment: Secure strike price based on support level for attractive premiums."
    )
    return recommendation, strike_price, dte

def show_recommendation_in_window(recommendation):
    """
    Displays the recommendation in a separate window.
    """
    def display_window():
        window = tk.Tk()
        window.title("Put Recommendation")
        window.geometry("400x300")

        text_area = ScrolledText(window, wrap=tk.WORD, font=("Arial", 12))
        text_area.pack(expand=True, fill=tk.BOTH)
        text_area.insert(tk.END, recommendation)
        text_area.configure(state="disabled")

        window.mainloop()

    threading.Thread(target=display_window).start()

def export_results_and_plot(recommendation, backtest_results, parameters, etf_name, folder="results", fig=None):
    """
    Exports the results to a file and saves the plot as an image with a timestamp and ETF name.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    monthyearstamp=datetime.now().strftime("%Y%m")
    
    safe_etf_name = etf_name.replace(" ", "_").replace("/", "_")
    results_filename = os.path.join(folder, f"results_{safe_etf_name}_{timestamp}.txt")
    plot_filename = os.path.join(folder, f"results_{safe_etf_name}_{timestamp}.png")
    recommendation_filename = os.path.join(folder, f"recommedation_{monthyearstamp}.txt")

    total_profit, avg_profit = backtest_results
    content = (
        f"Results exported on: {safe_etf_name} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Recommendation {safe_etf_name} :\n{recommendation}\n\n"
        f"Backtest Results:\n"
        f"  - Total Profit: {total_profit:.2f} USD\n"
        f"  - Average Profit: {avg_profit:.2f} USD\n\n"
        f"Parameters Used for selling puts on {safe_etf_name}:\n"
        f"  - Strike Price: {parameters['strike_price']:.2f} USD\n"
        f"  - Duration (DTE): {parameters['dte']} days\n"
    )
    
    rec_content = (
        f"#########################################################################################################\n"
        f"Results exported on: {safe_etf_name} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"Recommendation {safe_etf_name} :\n{recommendation}\n\n"
        f"Parameters Used for selling puts on {safe_etf_name}:\n"
        f"  - Strike Price: {parameters['strike_price']:.2f} USD\n"
        f"  - Duration (DTE): {parameters['dte']} days\n\n"
        f"*********************************************************************************************************\n"
    )

    # Save the results to a separate file
    with open(results_filename, "w") as file:
        file.write(content)
        
    print(f"Results successfully exported: {results_filename}")

    # Save the recommendation to a separate file
    with open(recommendation_filename, "a") as file:
        file.write(rec_content)
        
    print(f"Recommendation successfully exported: {recommendation_filename}")

    if fig:
        fig.savefig(plot_filename, dpi=300)
        print(f"Plot image successfully exported: {plot_filename}")

def export_results_to_html(recommendation, backtest_results, parameters, etf_name, folder="results", fig=None):
    """
    Exports the results to an HTML file and includes the plot image.
    """
    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_etf_name = etf_name.replace(" ", "_").replace("/", "_")
    html_filename = os.path.join(folder, f"results_{safe_etf_name}_{timestamp}.html")
    plot_filename = f"plot_{safe_etf_name}_{timestamp}.png"  # Relative path
    plot_filepath = os.path.join(folder, plot_filename)      # Full path

    total_profit, avg_profit = backtest_results

    # Save the plot as an image if provided
    if fig:
        fig.savefig(plot_filepath, dpi=300)
        print(f"Plot image successfully saved: {plot_filepath}")

    # Create HTML content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ETF Analysis Results - {safe_etf_name}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            h1 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
            table, th, td {{ border: 1px solid #ddd; }}
            th, td {{ padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .highlight {{ font-weight: bold; color: green; }}
            img {{ display: block; margin: 20px auto; max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <h1>ETF Analysis Results</h1>
        <h2>{safe_etf_name} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</h2>
        <h3>Recommendation</h3>
        <pre>{recommendation}</pre>
        <h3>Backtest Results</h3>
        <table>
            <tr>
                <th>Total Profit</th>
                <td class="highlight">${total_profit:.2f}</td>
            </tr>
            <tr>
                <th>Average Profit</th>
                <td class="highlight">${avg_profit:.2f}</td>
            </tr>
        </table>
        <h3>Parameters</h3>
        <table>
            <tr>
                <th>Strike Price</th>
                <td>${parameters['strike_price']:.2f}</td>
            </tr>
            <tr>
                <th>Duration (DTE)</th>
                <td>{parameters['dte']} days</td>
            </tr>
        </table>
        <h3>Generated Plot</h3>
        <img src="{plot_filename}" alt="ETF Analysis Plot">
    </body>
    </html>
    """

    # Save to an HTML file
    with open(html_filename, "w") as html_file:
        html_file.write(html_content)

    print(f"HTML export successfully saved: {html_filename}")

def plot_trends_and_backtest(selected_etf, selected_year):
    """
    Plots the chart with trends, RSI, Bollinger Bands, and support/resistance levels.
    """
    start_date = f'{selected_year-2}-01-01'
    end_date = f'{selected_year}-12-31'
    data = yf.download(selected_etf, start=start_date, end=end_date)

    if 'Close' not in data.columns:
        raise ValueError(f"The 'Close' column is missing from the downloaded data for {selected_etf}.")

    close_prices = clean_data(data[['Close']])
    data_for_year = data.loc[f'{selected_year-1}-01-01':f'{selected_year}-12-31']

    maxima_points, minima_points = detect_trends(data_for_year)
    resistance_levels = clean_data(maxima_points['Close']) if not maxima_points.empty else pd.Series([])
    support_levels = clean_data(minima_points['Close']) if not minima_points.empty else pd.Series([])

    trendline, slope = calculate_trendline(data_for_year)
    rolling_mean, upper_band, lower_band = calculate_bollinger_bands(data_for_year)
    moving_average_200 = data['Close'].rolling(window=200).mean()
    moving_average_200_value = float(moving_average_200.iloc[-1])
    iv = get_iv(selected_etf) or 0.0

    # Calculate RSI
    data_for_year = calculate_rsi(data_for_year)

    recommendation, strike_price, dte = generate_put_recommendation(data_for_year, support_levels, moving_average_200_value, iv)

    show_recommendation_in_window(recommendation)
    total_profit, avg_profit = backtest_strategy(data_for_year, strike_price=strike_price, dte=dte)

    parameters = {"strike_price": strike_price, "dte": dte}

    # Create plot
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12), gridspec_kw={'height_ratios': [3, 1]})

    # Upper plot: Price and indicators
    ax1.plot(data_for_year.index, close_prices.loc[data_for_year.index], label=f'{selected_etf} Closing Price', color='blue', alpha=0.6)
    ax1.plot(data_for_year.index, rolling_mean, label="20-Day Moving Average", color='black', linestyle='--', alpha=0.7)
    ax1.plot(data_for_year.index, upper_band, label="Upper Bollinger Band", color='purple', linestyle='--', alpha=0.7)
    ax1.plot(data_for_year.index, lower_band, label="Lower Bollinger Band", color='purple', linestyle='--', alpha=0.7)
    ax1.plot(data_for_year.index, moving_average_200.loc[data_for_year.index], label="200-Day Moving Average", color='cyan', linestyle='-', linewidth=1.5)
    ax1.plot(data_for_year.index, trendline, label=f"Trendline (Slope: {slope:.2f})", color='orange', linestyle='-')
 
    for level in resistance_levels:
        ax1.axhline(y=level, color='red', linestyle='--', alpha=0.7)
    for level in support_levels:
        ax1.axhline(y=level, color='green', linestyle='--', alpha=0.7)

    ax1.set_title(f"{selected_etf} Trends and Bollinger Bands ({selected_year})")
    ax1.set_ylabel('Price in USD')
    ax1.legend(loc='upper left')
    ax1.grid(True)

    # Lower plot: RSI
    ax2.plot(data_for_year.index, data_for_year['RSI'], label="RSI", color='darkblue', alpha=0.8)
    ax2.axhline(70, color='red', linestyle='--', alpha=0.7, label='Overbought (70)')
    ax2.axhline(30, color='green', linestyle='--', alpha=0.7, label='Oversold (30)')
    ax2.set_title('Relative Strength Index (RSI)')
    ax2.set_xlabel('Date')
    ax2.set_ylabel('RSI')
    ax2.legend(loc='upper left')
    ax2.grid(True)

    plt.tight_layout()

    export_results_and_plot(recommendation, (total_profit, avg_profit), parameters, selected_etf, fig=fig)
    export_results_to_html(recommendation, (total_profit, avg_profit), parameters, selected_etf, fig=fig)

    plt.show(block=False)
    plt.pause(0.1)

def start_selection_window():
    """
    Displays a selection window for ETF and year.
    """
    def on_submit():
        selected_etf = etf_selector.get()
        selected_year = int(year_selector.get())
        root.destroy()
        plot_trends_and_backtest(selected_etf, selected_year)

    root = tk.Tk()
    root.title("Select ETF and Year")
    root.geometry("400x200")

    tk.Label(root, text="Select ETF:").pack(pady=5)
    etf_selector = ttk.Combobox(root, values=["IWM", "SPY", "QQQ", "KWEB","ARKK"])
    etf_selector.set("IWM")
    etf_selector.pack(pady=5)

    tk.Label(root, text="Select Year:").pack(pady=5)
    year_selector = ttk.Combobox(root, values=[2020, 2021, 2022, 2023, 2024])
    year_selector.set("2024")
    year_selector.pack(pady=5)

    submit_button = tk.Button(root, text="Start", command=on_submit)
    submit_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_selection_window()
