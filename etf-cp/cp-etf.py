import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import empyrical as ep

def calculate_performance(tickers, benchmark='0050.TW', start_date=None, end_date=None):
    benchmark_data = yf.download(benchmark, start=start_date, end=end_date, progress=False)['Adj Close']
    benchmark_returns = benchmark_data.pct_change().dropna()
    
    results = []
    for ticker in tickers:
        try:
            stock_data = yf.download(ticker, start=start_date, end=end_date, progress=False)['Adj Close']
            stock_returns = stock_data.pct_change().dropna()
            
            metrics = {}
            # Remove '.TW' from the ticker symbol for display purposes
            metrics['ETF代號'] = ticker.replace('.TW', '')  
            metrics['年化報酬率 (%)'] = ep.annual_return(stock_returns) * 100  # Added (%)
            metrics['下檔風險 (%)'] = ep.downside_risk(stock_returns) * 100  # Added (%)
            metrics['sortino_ratio'] = ep.sortino_ratio(stock_returns)
            metrics['Max Drawdown (%)'] = ep.max_drawdown(stock_returns) * 100  # Added (%)
            metrics['Calmar Ratio'] = ep.calmar_ratio(stock_returns)
            metrics['Alpha (%)'] = ep.alpha(stock_returns, benchmark_returns) * 100  # Added (%)
            metrics['Beta (%)'] = ep.beta(stock_returns, benchmark_returns) * 100  # Added (%)
            metrics['總報酬 (%)'] = (stock_data.iloc[-1] / stock_data.iloc[0] - 1) * 100
            metrics['指標報酬 (%)'] = (benchmark_data.iloc[-1] / benchmark_data.iloc[0] - 1) * 100
            
            for key, value in metrics.items():
                if isinstance(value, (float, np.float64)):
                    metrics[key] = round(value, 2)
            
            results.append(metrics)
            
        except Exception as e:
            st.error(f"Error processing {ticker}: {str(e)}")
    
    return pd.DataFrame(results)

def main():
    st.title("ETF個股風險績效分析")

    # Date inputs
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("開始日期", value=datetime.now() - timedelta(days=365))
    with col2:
        end_date = st.date_input("結束日期", value=datetime.now())

    # Predefined list of tickers
    default_tickers = pd.read_pickle('hi_dvd.pkl')['yf_ticker'].tolist()
    
    # Allow user to input additional tickers
    user_tickers = st.text_input("新增比較標的 (comma-separated)", "")
    if user_tickers:
        additional_tickers = [ticker.strip() for ticker in user_tickers.split(',')]
        tickers = default_tickers + additional_tickers
    else:
        tickers = default_tickers

    if st.button("計算績效"):
        performance_df = calculate_performance(tickers, start_date=start_date, end_date=end_date)
        
        st.subheader("績效計算結果")
        st.dataframe(performance_df)

        # Download button for CSV
        csv = performance_df.to_csv(index=False)
        st.download_button(
            label="下載CSV檔",
            data=csv,
            file_name="etf_performance.csv",
            mime="text/csv",
        )

if __name__ == "__main__":
    main()
