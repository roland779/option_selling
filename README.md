
# Financial Data Analysis and Options Backtesting 
# ONLY FOR EDUCATIONAL PURPOSES

This repository provides Python scripts for analyzing financial market data, observing ETF performance, and logging option trades with integrated visualization and interactivity.

## Features

### ETF Analysis and Option Strategies (`option_selling_etf.py`):
- **Trend Detection**: Identifies upward and downward trends using local maxima and minima.
- **Bollinger Bands**: Calculates upper and lower Bollinger Bands for closing prices.
- **Trendline Calculation**: Uses linear regression to compute trendlines.
- **Implied Volatility (IV)**: Fetches IV data from Yahoo Finance options chains.
- **Backtesting**: Simulates a put-option trading strategy to analyze profitability.
- **Interactive GUI**: Allows users to select ETFs and specific years for analysis.
- **Visualization**: Plots trends, Bollinger Bands, support/resistance levels, and moving averages.

### Trade Logging (`options_selling_trade.py`):
- **Intuitive GUI**: Enter details of trades interactively.
- **Log Management**: Automatically saves trades in a monthly timestamped CSV file.
- **Calendar Integration**: Choose expiry dates using a calendar widget.

### Real-Time ETF Observation (`observer_etf.py`, `observer_options.py`):
- **Real-Time Data Refresh**: Fetches and updates daily ETF performance data.
- **Indicators**:
  - RSI (Relative Strength Index)
  - Historical Volatility
  - 200-day Moving Average
  - Implied Volatility (IV)
- **Dynamic Table View**: Interactive tables to view and sort ETF data.
- **Custom Visualization**: Color-coded changes in price and indicators like oversold/overbought conditions.

## Prerequisites

- Python 3.8 or later
- Required libraries:
  - `numpy`
  - `pandas`
  - `matplotlib`
  - `yfinance`
  - `scipy`
  - `scikit-learn`
  - `yahoo_fin`
  - `tkinter`
  - `tkcalendar`

You can install the required packages using pip:

```bash
pip install numpy pandas matplotlib yfinance scipy scikit-learn yahoo-fin tkcalendar
```

## How to Use

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/financial-data-analysis.git
   cd financial-data-analysis
   ```

2. Run the desired script based on the functionality:
   - **ETF Analysis and Backtesting**: 
     ```bash
     python option_selling_etf.py
     ```
   - **Log Option Trades**:
     ```bash
     python options_selling_trade.py
     ```
   - **Observe ETFs**:
     ```bash
     python observer_etf.py
     ```
   - **Observe Options Selling Data**:
     ```bash
     python observer_options.py
     ```

3. Follow on-screen instructions for each tool, including selecting ETFs, entering trade details, and reviewing live data.

## Example Outputs

### ETF Analysis
- **Visualization**: The script plots trends, Bollinger Bands, 200-day moving averages, and support/resistance levels.
- **Recommendation**: Displays a put-option recommendation based on support levels and IV in a separate window.
- **Backtesting Results**: Prints the total and average profits from the simulated trading strategy.

### Trade Logs
- Saved as CSV files in the `trades` folder with monthly timestamps.

### Real-Time Observation
- Displays an interactive table of real-time ETF data with dynamically updated prices, IV, and other indicators.

## Screenshots

- **SPY ETF Visualization**:
  ![SPY ETF Visualization](images/Figure_SPY.png)

- **IWM ETF Visualization**:
  ![IWM ETF Visualization](images/Figure_IWM.png)

## Contributing

Feel free to fork this repository and submit pull requests for improvements or new features. For major changes, please open an issue first to discuss your ideas.

### Collaboration and Suggestions

Contributions, feedback, and suggestions are always welcome! Whether it's a bug fix, a feature request, or an idea to improve the project, feel free to reach out or create an issue in the repository.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- [Yahoo Finance API](https://pypi.org/project/yfinance/)
- [Yahoo Fin](https://theautomatic.net/yahoo_fin-documentation/) for options data
- Inspired by common financial analysis and trading strategies.

---
Ensure all configurations and dependencies are correctly set before running the scripts for best performance.
