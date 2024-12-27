import yfinance as yf
import pandas as pd
import tkinter as tk
from tkinter import ttk
import numpy as np
import time

############################################################################################################
# Observe ETFs and their data
############################################################################################################

# Define the list of ETFs to track
etfs = ["IWM", "SPY", "QQQ", "KWEB", "ARKK"]

# Function to fetch daily price and implied volatility (IV) data
def fetch_etf_data(symbol):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1y", interval="1d")
        hist.reset_index(inplace=True)
        hist = hist[["Date", "Close"]]
        hist.columns = ["Date", "Close Price"]

        # Calculate 200-day moving average
        hist["200-Day MA"] = hist["Close Price"].rolling(window=200).mean()

        # Calculate RSI (Relative Strength Index)
        delta = hist["Close Price"].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        hist["RSI"] = 100 - (100 / (1 + rs))

        # Calculate Historical Volatility
        hist["Log Returns"] = np.log(hist["Close Price"] / hist["Close Price"].shift(1))
        hist["Hist Volatility"] = hist["Log Returns"].rolling(window=21).std() * np.sqrt(252)

        # Fetch Current IV (if available)
        try:
            options = ticker.option_chain()
            iv = options.calls["impliedVolatility"].mean() if not options.calls.empty else None
        except Exception as opt_err:
            print(f"Error fetching IV for {symbol}: {opt_err}")
            iv = None

        return hist, iv
    except Exception as e:
        print(f"Error fetching data for {symbol}: {e}")
        return None, None

# Fetch data for all ETFs
data = {}
iv_data = {}

def refresh_data():
    global data, iv_data
    data = {}
    iv_data = {}
    for etf in etfs:
        print(f"Fetching data for {etf}...")
        price_data, iv = fetch_etf_data(etf)
        if price_data is not None:
            data[etf] = price_data
            iv_data[etf] = iv
    print(f"Fetching data done - {time.strftime('%H:%M:%S')}")

def show_data_table():
    root = tk.Tk()
    root.title("ETF Tracker")
    root.geometry("1400x500+300+100")  # Adjusted size for additional column

    # Create a custom style for the Treeview header
    style = ttk.Style(root)
    style.configure(
        "Treeview.Heading",
        font=("Helvetica", 12, "bold"),  # Font size and bold
        background="lightblue",         # Background color
        foreground="black",             # Text color
    )

    columns = ("ETF", "Date", "Close Price", "Change", "200-Day MA", "RSI", "Indicator", "IV", "Hist Volatility")
    tree = ttk.Treeview(root, columns=columns, show="headings")

    # Define column headers and sorting functionality
    for col in columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        tree.column(col, width=150, anchor="center")

    tree.pack(fill=tk.BOTH, expand=True)

    def sort_column(tree, col, reverse):
        data_list = [(tree.set(child, col), child) for child in tree.get_children("")]
        try:
            data_list.sort(key=lambda t: float(t[0].strip("$").replace(",", "")), reverse=reverse)
        except ValueError:
            data_list.sort(reverse=reverse)

        for index, (_, child) in enumerate(data_list):
            tree.move(child, "", index)

        tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

    def update_table():
        for row in tree.get_children():
            tree.delete(row)

        for etf, df in data.items():
            iv = iv_data[etf]
            if not df.empty:
                today = df.iloc[-1]
                yesterday = df.iloc[-2] if len(df) > 1 else None
                change = today["Close Price"] - (yesterday["Close Price"] if yesterday is not None else 0)

                indicator = "Neutral"
                if today["RSI"] < 30:
                    indicator = "Oversold"
                elif today["RSI"] > 70:
                    indicator = "Overbought"

                tags = ("positive" if change >= 0 else "negative",)

                # Ensure Hist Volatility is displayed as a percentage
                hist_vol = f"{today['Hist Volatility']:.2%}" if not pd.isna(today["Hist Volatility"]) else "N/A"

                tree.insert(
                    "",
                    tk.END,
                    values=(
                        etf,
                        today["Date"].strftime("%Y-%m-%d"),
                        f"${today['Close Price']:.2f}",
                        f"${change:.2f}",
                        f"${today['200-Day MA']:.2f}" if not pd.isna(today["200-Day MA"]) else "N/A",
                        f"{today['RSI']:.2f}" if not pd.isna(today["RSI"]) else "N/A",
                        indicator,
                        f"{iv:.2%}" if iv else "N/A",
                        hist_vol
                    ),
                    tags=tags
                )

        tree.tag_configure("positive", foreground="green")
        tree.tag_configure("negative", foreground="red")

        root.after(60000, refresh_and_update)

    def refresh_and_update():
        refresh_data()
        update_table()

    refresh_and_update()
    root.mainloop()

# Run the application
refresh_data()
show_data_table()
