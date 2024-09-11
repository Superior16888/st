import yfinance as yf
import quantstats as qs
import streamlit as st
import datetime
import warnings
import os

# Suppress warnings
warnings.filterwarnings("ignore")

# Set the Streamlit app layout to wide mode for better alignment
st.set_page_config(layout="wide")

# Streamlit App title
st.title("Stock Performance Analysis with QuantStats")

# Input for stock symbol and benchmark
stock_symbol = st.text_input("Enter the stock symbol (e.g., 0056.TW)", "0056.TW")
benchmark_symbol = st.text_input("Enter the benchmark symbol (e.g., ^TWII for Taiwan Index)", "0050.TW")

# Input for number of years
years = st.number_input("Enter the number of years of historical data", min_value=1, max_value=20, value=10)

# Button to trigger the report generation
if st.button('Generate Report'):
    # Calculate the start and end dates based on the specified number of years
    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * years)).strftime("%Y-%m-%d")

    # Download stock and benchmark data
    if stock_symbol and benchmark_symbol:
        st.write(f"Fetching data for {stock_symbol} from {start_date} to {end_date}...")
        data = yf.download(stock_symbol, start=start_date, end=end_date)
        benchmark_data = yf.download(benchmark_symbol, start=start_date, end=end_date)
        
        if not data.empty:
            # Calculate the daily returns
            returns = data["Adj Close"].pct_change().dropna()
            benchmark_returns = benchmark_data["Adj Close"].pct_change().dropna()            

            # Generate QuantStats report
            st.write(f"Generating report for {stock_symbol}...")

            # Save the QuantStats report to an HTML file
            report_file = f"{stock_symbol}_performance_report.html"
            qs.reports.html(returns, benchmark=benchmark_returns, title=f"{stock_symbol} 績效報告", benchmark_title=f"{benchmark_symbol}", output=report_file)

            # Provide a download link for the generated report
            with open(report_file, "rb") as file:
                btn = st.download_button(
                    label="Download Performance Report",
                    data=file,
                    file_name=report_file,
                    mime="text/html"
                )

            st.success(f"Report generated successfully! Click the button above to download.")

            # Clean up the file after providing the download link
            os.remove(report_file)
        else:
            st.write(f"No data found for {stock_symbol}. Please check the symbol and try again.")