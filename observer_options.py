import tkinter as tk
from tkinter import messagebox, ttk
import csv
import os
from datetime import datetime
import yfinance as yf

############################################################################################################
# Observe Logged Trades with Current Price and Sortable Columns
############################################################################################################

def load_trade_log():
    """
    Loads the trade log from the CSV file for the current month.
    """
    folder = "trades"
    timestamp = datetime.now().strftime("%Y%m")
    log_file = os.path.join(folder, f"option_log_{timestamp}.csv")

    if not os.path.exists(log_file):
        messagebox.showwarning("No Trades Logged", "No trades have been logged for the current month.")
        return []

    with open(log_file, mode="r") as file:
        reader = csv.reader(file)
        trades = list(reader)

        # Separate headers and data
        if trades:
            headers = trades[0]
            data = trades[1:]
            return headers, data
        else:
            return [], []

def get_current_price(symbol):
    """
    Fetches the current price of the symbol using yfinance.
    """
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]
        return price
    except Exception as e:
        print(f"Error fetching current price for {symbol}: {e}")
        return None

def sort_column(tree, col, reverse):
    """
    Sorts the treeview by a specific column.
    """
    data_list = [(tree.set(child, col), child) for child in tree.get_children("")]
    try:
        data_list.sort(key=lambda t: float(t[0].strip("$").replace(",", "")) if t[0].replace(".", "").replace("$", "").isdigit() else t[0], reverse=reverse)
    except ValueError:
        data_list.sort(reverse=reverse)

    for index, (_, child) in enumerate(data_list):
        tree.move(child, "", index)

    tree.heading(col, command=lambda: sort_column(tree, col, not reverse))

def refresh_data(tree, headers):
    """
    Refreshes the data in the table.
    """
    # Clear the table
    for row in tree.get_children():
        tree.delete(row)

    headers, trades = load_trade_log()
    for trade in trades:
        symbol = trade[4]  # Assuming Symbol is the 5th column
        strike_price = float(trade[6])  # Assuming Strike Price is the 7th column

        # Fetch the current price
        current_price = get_current_price(symbol)
        current_price_display = f"${current_price:.2f}" if current_price else "N/A"

        # Check the condition and tag the row
        if current_price and current_price > strike_price:
            tags = ("above_strike",)
        else:
            tags = ("below_strike",)

        trade.append(current_price_display)  # Add new data to the row
        tree.insert("", tk.END, values=trade, tags=tags)

    # Configure row colors
    tree.tag_configure("above_strike", background="lightgreen")
    tree.tag_configure("below_strike", background="lightcoral")

def display_trade_log():
    """
    Displays the logged trades in a table using Tkinter and highlights rows based on conditions.
    """
    headers, trades = load_trade_log()
    if not trades:
        return

    root = tk.Tk()
    root.title("Trade Log Viewer")
    root.geometry("1000x600")

    # Add a new column for "Current Price"
    headers.append("Current Price")
    tree = ttk.Treeview(root, columns=headers, show="headings")
    for col in headers:
        tree.heading(col, text=col, command=lambda c=col: sort_column(tree, c, False))
        tree.column(col, anchor="center", width=120)

    tree.pack(fill=tk.BOTH, expand=True)

    # Initial data load
    refresh_data(tree, headers)

    # Set up periodic refresh (every 30 seconds)
    def periodic_refresh():
        refresh_data(tree, headers)
        print("Refreshed data - observed trades " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))   
        root.after(30000, periodic_refresh)  # Schedule the next refresh in 30 seconds

    periodic_refresh()
    root.mainloop()

if __name__ == "__main__":
    display_trade_log()
