import tkinter as tk
from tkinter import messagebox
from tkcalendar import Calendar
import csv
from datetime import datetime
import os
import pandas as pd

def log_put_option_trade_to_html(date, time, action, quantity, symbol, expiry, strike_price, option_type, price, comment):
    """
    Logs a put option trade to a CSV file and exports it to a well-formatted HTML webpage.
    """
    folder = "trades"
    if not os.path.exists(folder):
        os.makedirs(folder)

    timestamp = datetime.now().strftime("%Y%m")
    log_file = os.path.join(folder, f"option_log_{timestamp}.csv")
    html_file = os.path.join(folder, f"option_log_{timestamp}.html")

    headers = ["Date", "Time", "Action", "Quantity", "Symbol", "Expiry", "Strike Price", "Option Type", "Price", "Comment"]
    entry = [date, time, action, quantity, symbol, expiry, strike_price, option_type, price, comment]

    # Check if the log file exists and write headers if needed
    file_exists = os.path.isfile(log_file)

    with open(log_file, mode='a', newline='') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(headers)  # Write headers only for a new file
        writer.writerow(entry)  # Write the trade entry

    print(f"Trade logged: {entry}")

    # Convert CSV to a well-formatted HTML file
    try:
        df = pd.read_csv(log_file)
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Trade Log - {timestamp}</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 20px;
                    background-color: #f4f4f9;
                    color: #333;
                }}
                h1 {{
                    color: #007bff;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    text-align: left;
                    padding: 8px;
                }}
                th {{
                    background-color: #007bff;
                    color: white;
                }}
                tr:nth-child(even) {{
                    background-color: #f9f9f9;
                }}
                tr:hover {{
                    background-color: #f1f1f1;
                }}
            </style>
        </head>
        <body>
            <h1>Trade Log for {timestamp}</h1>
            <table>
                <thead>
                    <tr>
                        {''.join(f"<th>{col}</th>" for col in headers)}
                    </tr>
                </thead>
                <tbody>
        """
        for _, row in df.iterrows():
            html_content += "<tr>" + "".join(f"<td>{value}</td>" for value in row) + "</tr>\n"

        html_content += """
                </tbody>
            </table>
        </body>
        </html>
        """

        with open(html_file, "w", encoding="utf-8") as file:
            file.write(html_content)

        print(f"Trades exported to HTML: {html_file}")

    except Exception as e:
        print(f"Error exporting to HTML: {e}")

def open_calendar():
    """
    Opens a calendar to select the expiry date.
    """
    def select_date():
        selected_date = cal.get_date()  # Get the selected date
        expiry_entry.delete(0, tk.END)  # Clear current value
        expiry_entry.insert(0, selected_date)  # Insert selected date directly
        calendar_window.destroy()  # Close calendar window

    calendar_window = tk.Toplevel(trade_window)
    calendar_window.title("Select Expiry Date")
    calendar_window.geometry("300x300")

    cal = Calendar(calendar_window, date_pattern="yyyy-mm-dd")  # Use the standard YYYY-MM-DD format
    cal.pack(pady=20)

    select_button = tk.Button(calendar_window, text="Select Date", command=select_date)
    select_button.pack(pady=10)

def open_trade_entry_window():
    """
    Opens a window to allow the user to enter a trade.
    """
    def submit_trade():
        try:
            # Collect user inputs
            date = date_entry.get()
            time = time_entry.get()
            action = action_var.get()
            quantity = int(quantity_entry.get())
            symbol = symbol_entry.get()
            expiry = expiry_entry.get()
            strike_price = float(strike_price_entry.get())
            option_type = option_type_var.get()
            price = float(price_entry.get())
            comment = comment_entry.get("1.0", tk.END).strip()

            # Log the trade and export to HTML
            log_put_option_trade_to_html(date, time, action, quantity, symbol, expiry, strike_price, option_type, price, comment)

            # Show success message
            messagebox.showinfo("Trade Logged", f"Trade successfully logged and exported:\n\n{action} {quantity} {symbol} {option_type} {expiry} {strike_price} @ {price}\nComment: {comment}")

        except ValueError as e:
            messagebox.showerror("Input Error", "Please ensure all fields are filled correctly.\n" + str(e))

    # Create the trade entry window
    global trade_window, expiry_entry  # Define global variables for calendar interaction
    trade_window = tk.Tk()
    trade_window.title("Enter Trade")
    trade_window.geometry("400x900")

    # Add input fields
    tk.Label(trade_window, text="Date (YYYY-MM-DD):").pack(pady=5)
    date_entry = tk.Entry(trade_window)
    date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))  # Default to today's date
    date_entry.pack(pady=5)

    tk.Label(trade_window, text="Time (HH:MM):").pack(pady=5)
    time_entry = tk.Entry(trade_window)
    time_entry.insert(0, datetime.now().strftime("%H:%M"))  # Default to current time
    time_entry.pack(pady=5)

    tk.Label(trade_window, text="Action:").pack(pady=5)
    action_var = tk.StringVar(value="SOLD")
    action_menu = tk.OptionMenu(trade_window, action_var, "SOLD", "BOUGHT", "REC SOLD")
    action_menu.pack(pady=5)

    tk.Label(trade_window, text="Quantity:").pack(pady=5)
    quantity_entry = tk.Entry(trade_window)
    quantity_entry.insert(0, "1")
    quantity_entry.pack(pady=5)

    tk.Label(trade_window, text="Symbol:").pack(pady=5)
    symbol_entry = tk.Entry(trade_window)
    symbol_entry.insert(0, "IWM")
    symbol_entry.pack(pady=5)

    tk.Label(trade_window, text="Expiry (YYYY-MM-DD):").pack(pady=5)
    expiry_entry = tk.Entry(trade_window)
    expiry_entry.pack(pady=5)
    tk.Button(trade_window, text="Select Expiry Date", command=open_calendar).pack(pady=5)

    tk.Label(trade_window, text="Strike Price:").pack(pady=5)
    strike_price_entry = tk.Entry(trade_window)
    strike_price_entry.pack(pady=5)

    tk.Label(trade_window, text="Option Type:").pack(pady=5)
    option_type_var = tk.StringVar(value="PUT")
    option_type_menu = tk.OptionMenu(trade_window, option_type_var, "PUT", "CALL")
    option_type_menu.pack(pady=5)

    tk.Label(trade_window, text="Price:").pack(pady=5)
    price_entry = tk.Entry(trade_window)
    price_entry.pack(pady=5)

    tk.Label(trade_window, text="Comments:").pack(pady=5)
    comment_entry = tk.Text(trade_window, height=5, width=40)
    comment_entry.pack(pady=5)

    # Submit button
    submit_button = tk.Button(trade_window, text="Log Trade", command=submit_trade)
    submit_button.pack(pady=20)

    trade_window.mainloop()

if __name__ == "__main__":
    open_trade_entry_window()
