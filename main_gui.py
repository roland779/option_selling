import tkinter as tk
from tkinter import messagebox
import subprocess
import os

def start_etf_analysis():
    """Launches the ETF Analysis module."""
    try:
        venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python")
        script_path = os.path.join(os.getcwd(), "option_selling", "option_selling_strategy_etf.py")
        subprocess.Popen([venv_python, script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start ETF Analysis: {e}")

def log_option_trades():
    """Launches the Option Trades Logging module."""
    try:
        venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python")
        script_path = os.path.join(os.getcwd(), "option_selling", "options_selling_trade.py")
        subprocess.Popen([venv_python, script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Trade Logging: {e}")

def observe_etfs():
    """Launches the ETF Observation module."""
    try:
        venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python")
        script_path = os.path.join(os.getcwd(), "option_selling", "observer_etf.py")
        subprocess.Popen([venv_python, script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start ETF Observation: {e}")

def observe_options():
    """Launches the Option Observation module."""
    try:
        venv_python = os.path.join(os.getcwd(), ".venv", "Scripts", "python")
        script_path = os.path.join(os.getcwd(), "option_selling", "observer_options.py")
        subprocess.Popen([venv_python, script_path])
    except Exception as e:
        messagebox.showerror("Error", f"Failed to start Options Observation: {e}")

# Create the main window
root = tk.Tk()
root.title("Financial Analysis Tool")
root.geometry("400x300")

# Header label
header_label = tk.Label(root, text="Welcome to the Financial Analysis Tool", font=("Helvetica", 14, "bold"))
header_label.pack(pady=20)

# Buttons for each module
btn_etf_analysis = tk.Button(root, text="Start ETF Analysis", font=("Helvetica", 12), command=start_etf_analysis)
btn_etf_analysis.pack(pady=10)

btn_trade_logging = tk.Button(root, text="Log Option Trades", font=("Helvetica", 12), command=log_option_trades)
btn_trade_logging.pack(pady=10)

btn_etf_observation = tk.Button(root, text="Observe ETFs", font=("Helvetica", 12), command=observe_etfs)
btn_etf_observation.pack(pady=10)

btn_options_observation = tk.Button(root, text="Observe Options", font=("Helvetica", 12), command=observe_options)
btn_options_observation.pack(pady=10)

# Run the main loop
root.mainloop()
