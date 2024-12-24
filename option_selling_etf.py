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
        series = series.squeeze()  # Convert single-column DataFrame to Series
    elif isinstance(series, np.ndarray) and series.ndim > 1:
        series = pd.Series(series.ravel())  # Flatten multi-dimensional arrays
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

def calculate_trendline(data):
    """
    Calculates the trendline based on closing prices.
    """
    data = data.reset_index()  # Reset index to use date values
    x = np.arange(len(data)).reshape(-1, 1)  # Index as independent variable
    y = data['Close'].values  # Closing prices as dependent variable

    # Linear regression
    model = LinearRegression()
    model.fit(x, y)
    trendline = model.predict(x)
    slope = float(model.coef_[0])  # Extract slope as float
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
    close_prices = data['Close'].values  # Extract closing prices as a NumPy array

    for i in range(len(close_prices) - dte):
        option_start_price = close_prices[i]
        option_end_price = close_prices[i + dte]  # Ensure float by direct access

        # Simulation: Option expires worthless if price stays above the strike price
        if float(option_end_price) >= float(strike_price):
            profit = option_start_price * 0.02  # Hypothetical premium: 2% of the starting price
        else:
            # Option exercised: Difference recorded as loss
            profit = strike_price - option_end_price

        profits.append(profit)

    # Summarize results
    total_profit = np.sum(profits)
    avg_profit = np.mean(profits) if profits else 0

    return total_profit, avg_profit

def generate_put_recommendation(data, support_levels, moving_average_200, iv):
    """
    Generates a put recommendation based on support levels and IV.
    """
    if support_levels.empty:
        return "No support levels found. Recommendation not possible."

    current_price = float(data['Close'].iloc[-1])  # Current closing price
    nearest_support = min(support_levels, key=lambda x: abs(current_price - x))
    strike_price = round(nearest_support * 0.95, 2)  # Safety margin 5% below support level
    dte = 45  # Default to 45 days

    recommendation = (
        f"Current Price: {current_price:.2f} USD\n"
        f"Nearest Support: {nearest_support:.2f} USD\n"
        f"200-Day Average: {moving_average_200:.2f} USD\n"
        f"Recommended Strike Price: {strike_price:.2f} USD\n"
        f"Recommended Duration (DTE): {dte} days\n"
        f"Implied Volatility (IV): {iv:.2%}\n"
        "Comment: Secure strike price based on support level for attractive premiums."
    )
    print(recommendation)
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

def plot_trends_and_backtest(selected_etf, selected_year):
    """
    Plots the chart with trends, breakouts, Bollinger Bands, and support/resistance levels.
    """
    start_date = f'{selected_year-1}-01-01'
    end_date = f'{selected_year}-12-31'
    data = yf.download(selected_etf, start=start_date, end=end_date)

    if 'Close' not in data.columns:
        raise ValueError(f"The 'Close' column is missing from the downloaded data for {selected_etf}.")

    close_prices = clean_data(data[['Close']])
    data_for_year = data.loc[f'{selected_year}-01-01':f'{selected_year}-12-31']

    maxima_points, minima_points = detect_trends(data_for_year)
    resistance_levels = clean_data(maxima_points['Close']) if not maxima_points.empty else pd.Series([])
    support_levels = clean_data(minima_points['Close']) if not minima_points.empty else pd.Series([])

    trendline, slope = calculate_trendline(data_for_year)
    rolling_mean, upper_band, lower_band = calculate_bollinger_bands(data_for_year)
    moving_average_200 = data['Close'].rolling(window=200).mean()
    moving_average_200_value = float(moving_average_200.iloc[-1])
    iv = get_iv(selected_etf) or 0.0
    recommendation, strike_price, dte = generate_put_recommendation(data_for_year, support_levels, moving_average_200_value, iv)

    show_recommendation_in_window(recommendation)
    total_profit, avg_profit = backtest_strategy(data_for_year, strike_price=strike_price, dte=dte)
    print(f"Backtest Results:\nTotal Profit: {total_profit:.2f} USD\nAverage Profit: {avg_profit:.2f} USD")
    print(f"Parameters Used:\nStrike Price: {strike_price:.2f} USD\nDuration: {dte} days")

    plt.ion()
    fig, ax = plt.subplots(figsize=(16, 10))
    ax.plot(data_for_year.index, close_prices.loc[data_for_year.index], label=f'{selected_etf} Closing Price', color='blue', alpha=0.6)
    ax.plot(data_for_year.index, rolling_mean, label="20-Day Moving Average", color='black', linestyle='--', alpha=0.7)
    ax.plot(data_for_year.index, upper_band, label="Upper Bollinger Band", color='purple', linestyle='--', alpha=0.7)
    ax.plot(data_for_year.index, lower_band, label="Lower Bollinger Band", color='purple', linestyle='--', alpha=0.7)
    ax.plot(data_for_year.index, moving_average_200.loc[data_for_year.index], label="200-Day Moving Average", color='cyan', linestyle='-', linewidth=1.5)

    for level in resistance_levels:
        ax.axhline(y=level, color='red', linestyle='--', alpha=0.7)
    for level in support_levels:
        ax.axhline(y=level, color='green', linestyle='--', alpha=0.7)

    ax.plot(data_for_year.index, trendline, label=f"Trendline (Slope: {slope:.2f})", color='orange', linestyle='-')
    ax.set_title(f'{selected_etf} Trends, Breakouts, Bollinger Bands and 200-Day Moving Average ({selected_year})')
    ax.set_xlabel('Date')
    ax.set_ylabel('Price in USD')
    ax.legend(loc='upper left')
    ax.grid(True)
    plt.tight_layout()
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
    etf_selector = ttk.Combobox(root, values=["IWM", "SPY", "QQQ", "KWEB"])
    etf_selector.set("IWM")
    etf_selector.pack(pady=5)

    tk.Label(root, text="Select Year:").pack(pady=5)
    year_selector = ttk.Combobox(root, values=[2020,2021, 2022, 2023, 2024])
    year_selector.set("2024")
    year_selector.pack(pady=5)

    submit_button = tk.Button(root, text="Start", command=on_submit)
    submit_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    start_selection_window()