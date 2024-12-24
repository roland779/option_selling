# option_selling
Python program for financial data analysis: includes trend detection, Bollinger Bands, trendline calculation, options backtesting, and trading recommendations with an interactive GUI.

Financial Data Analysis and Options Backtesting

This repository contains a Python script for analyzing financial market data, detecting trends, and providing trading recommendations based on support levels, Bollinger Bands, and implied volatility (IV). The script also includes an interactive graphical user interface (GUI) for enhanced usability.
Features

    Trend Detection: Identifies upward and downward trends using local maxima and minima.
    Bollinger Bands: Calculates upper and lower Bollinger Bands for closing prices.
    Trendline Calculation: Uses linear regression to compute trendlines.
    Implied Volatility (IV): Fetches IV data from Yahoo Finance options chains.
    Backtesting: Simulates a put-option trading strategy to analyze profitability.
    Interactive GUI: Allows users to select ETFs and specific years for analysis.
    Visualization: Plots trends, Bollinger Bands, support/resistance levels, and moving averages.

Prerequisites

    Python 3.8 or later
    Required libraries:
        numpy
        pandas
        matplotlib
        yfinance
        scipy
        sklearn
        yahoo_fin
        tkinter

You can install the required packages using pip:

pip install numpy pandas matplotlib yfinance scipy scikit-learn yahoo-fin

How to Use

    Clone the repository:

git clone https://github.com/yourusername/financial-data-analysis.git
cd financial-data-analysis

Run the script:

    python main.py

    Select an ETF and a year in the interactive GUI to analyze trends and get trading recommendations.

Example Output

    Visualization: The script plots trends, Bollinger Bands, 200-day moving averages, and support/resistance levels.
    Recommendation: Displays a put-option recommendation based on support levels and IV in a separate window.
    Backtesting Results: Prints the total and average profits from the simulated trading strategy.

Screenshots

Add screenshots of the GUI and visualizations here.
Contributing

Feel free to fork this repository and submit pull requests for improvements or new features. For major changes, please open an issue first to discuss your ideas.
License

This project is licensed under the MIT License - see the LICENSE file for details.
Acknowledgements

    Yahoo Finance API
    Yahoo Fin for options data
    Inspired by common financial analysis and trading strategies.
