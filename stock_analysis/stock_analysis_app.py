import yfinance as yf
import quantstats as qs
import streamlit as st
import datetime
import warnings
import pandas as pd
import base64

# Suppress warnings
warnings.filterwarnings("ignore")

# Set the Streamlit app layout to wide mode for better alignment
st.set_page_config(layout="wide")

# Streamlit App title
st.title("Stock Performance Analysis with QuantStats")

# Input for stock symbol and benchmark
stock_symbol = st.text_input("Enter the stock symbol (e.g., 0050.TW)", "0050.TW")
benchmark_symbol = st.text_input("Enter the benchmark symbol (e.g., ^TWII for Taiwan Index)", "^TWII")

# Input for number of years
years = st.number_input("Enter the number of years of historical data", min_value=1, max_value=20, value=10)

def get_binary_file_downloader_html(bin_file, file_label='File'):
    with open(bin_file, 'rb') as f:
        data = f.read()
    bin_str = base64.b64encode(data).decode()
    href = f'<a href="data:application/octet-stream;base64,{bin_str}" download="{file_label}">Download {file_label}</a>'
    return href

# Button to trigger the report generation
if st.button('Generate Report'):
    # Calculate the start and end dates based on the specified number of years
    end_date = datetime.datetime.today().strftime("%Y-%m-%d")
    start_date = (datetime.datetime.today() - datetime.timedelta(days=365 * years)).strftime("%Y-%m-%d")

    # Download stock and benchmark data
    if stock_symbol and benchmark_symbol:
        st.write(f"Fetching data for {stock_symbol} from {start_date} to {end_date}...")
        try:
            # Disable progress bar in yfinance
            yf.pdr_override()
            data = yf.download(stock_symbol, start=start_date, end=end_date, progress=False)
            benchmark_data = yf.download(benchmark_symbol, start=start_date, end=end_date
                                         
            if not data.empty:
                # Calculate the daily returns
                returns = data["Adj Close"].pct_change().dropna()
                benchmark_returns = benchmark_data["Adj Close"].pct_change().dropna() 
                # Generate QuantStats report
                st.write(f"Generating report for {stock_symbol}...")
                # Save the QuantStats report to an HTML file
                report_file = f"{stock_symbol}_quantstats_report.html"
                #qs.reports.html(returns, benchmark=benchmark_returns, output=report_file, title=f"{stock_symbol} 績效報告" ,benchmark_title=f"{benchmark_symbol}")
                qs.reports.html(returns, 
                benchmark=benchmark_returns, 
                output=report_file, 
                title=f"{stock_symbol} 績效報告", 
                benchmark_title=f"{benchmark_symbol}")
                # Provide download link
                st.markdown(get_binary_file_downloader_html(report_file, f'{stock_symbol}_report.html'), unsafe_allow_html=True)
                
                st.success("Report generated successfully. Click the link above to download.")
            else:
                st.write(f"No data found for {stock_symbol}. Please check the symbol and try again.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.write("Please try again with a different stock symbol or date range.")
