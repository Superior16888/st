import yfinance as yf
import quantstats as qs
import streamlit as st
import datetime
import warnings

# Suppress warnings
warnings.filterwarnings("ignore")

# Set the Streamlit app layout to wide mode for better alignment
st.set_page_config(layout="wide")

# Inject custom CSS to center the report
st.markdown(
    """
    <style>
    .centered {
        display: flex;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True
)

# Streamlit App title
st.title("Stock Performance Analysis with QuantStats")

# Input for stock symbol and benchmark
stock_symbol = st.text_input("Enter the stock symbol (e.g., 0050.TW)", "0050.TW")
benchmark_symbol = st.text_input("Enter the benchmark symbol (e.g., ^TWII for Taiwan Index)", "^TWII")

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
            report_file = "quantstats-tearsheet.html"
                qs.reports.html(
                returns, 
                benchmark=benchmark_returns, 
                output=report_file, 
                title=f"{stock_symbol} 績效報告", 
                benchmark_title=f"{benchmark_symbol}"
            )
            # Read the HTML file and display it in the Streamlit app
            with open(report_file, "r", encoding="utf-8") as file:
                report_html = file.read()

            # Center the QuantStats report using a div with 'centered' class
            st.markdown('<div class="centered">', unsafe_allow_html=True)
            st.components.v1.html(report_html, width=1200, height=6000, scrolling=True)
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.write(f"No data found for {stock_symbol}. Please check the symbol and try again.")
