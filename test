import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
import time

def get_stock_data(symbol, start_date, end_date, max_retries=5, retry_delay=5):
    """
    Fetch stock data with retry mechanism
    """
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            dividends = stock.dividends
            if not data.empty and not dividends.empty:
                return stock, data, dividends
        except Exception as e:
            st.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                st.info(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                st.error("Failed to fetch data after multiple attempts.")
                return None, None, None
    return None, None, None

def analyze_dividend_strategy(symbol, before_days, after_days, dividend_tax_rate, years=10):
    """
    Analyze dividend strategy returns, including transaction costs
    """
    tz = pytz.timezone('Asia/Taipei')
    end_date = datetime.now(tz)
    start_date = end_date - timedelta(days=365*years)
    
    stock, data, dividends = get_stock_data(symbol, start_date, end_date)
    if stock is None or data is None or dividends is None:
        return None, 0, []
    
    ex_dividend_dates = dividends.index.tz_convert(tz).tolist()
    ex_dividend_dates = [date for date in ex_dividend_dates if date >= start_date]
    
    transaction_fee_rate = 0.001425 * 0.28
    transaction_tax_rate = 0.001
    
    returns = []
    
    for ex_div_date in ex_dividend_dates:
        buy_date = ex_div_date - timedelta(days=before_days)
        sell_date = ex_div_date + timedelta(days=after_days)
        
        buy_dates = data.index[data.index <= buy_date]
        sell_dates = data.index[data.index >= sell_date]
        
        if len(buy_dates) == 0 or len(sell_dates) == 0:
            continue
        
        buy_date = buy_dates[-1]
        sell_date = sell_dates[0]
        
        buy_price = data.loc[buy_date, 'Close']
        sell_price = data.loc[sell_date, 'Close']
        
        buy_cost = buy_price * (1 + transaction_fee_rate)
        sell_proceeds = sell_price * (1 - transaction_fee_rate - transaction_tax_rate)
        
        dividend_amount = dividends.loc[ex_div_date]
        after_tax_dividend = dividend_amount * (1 - dividend_tax_rate)
        
        total_return = (sell_proceeds - buy_cost + after_tax_dividend) / buy_cost
        
        returns.append((ex_div_date, total_return))
    
    if not returns:
        return None, 0, []
    
    avg_return = sum(return_value for _, return_value in returns) / len(returns)
    return avg_return, len(returns), returns

st.title('股票除息策略分析')

symbol = st.text_input('輸入股票代碼，上市股票加.TW;上櫃加.TWO (例如: 2330.TW 或 00720B.TWO)', '2330.TW')
before_days = st.number_input('除息日前幾天買入', min_value=1, value=20)
after_days = st.number_input('除息日後幾天賣出', min_value=1, value=20)
dividend_tax_rate = st.number_input('股息稅率 (%)', min_value=0, max_value=100, value=8) / 100
years = st.number_input('分析年數', min_value=1, max_value=20, value=10)

if st.button('進行分析'):
    with st.spinner('正在分析中...'):
        result = analyze_dividend_strategy(symbol, before_days, after_days, dividend_tax_rate, years)
    
    if result[0] is None:
        st.error(f"警告：資料抓取錯誤或在指定的{years}年內沒有找到可分析的除息事件")
    else:
        avg_return, event_count, detailed_returns = result
        
        st.success('分析完成！')
        st.write('除息策略歷史總報酬率')
        chart_data = pd.DataFrame(
            {'除息日': [date for date, _ in detailed_returns],
             '回報率': [return_value for _, return_value in detailed_returns]}
        )
        st.bar_chart(chart_data.set_index('除息日'))
  
        st.write(f"股票代碼: {symbol}")
        st.write(f"分析策略: 除息日前{before_days}天買入，除息日後{after_days}天賣出")
        st.write(f"股息稅率: {dividend_tax_rate*100:.1f}%")
        st.write("交易手續費: 0.1425% (享72%折扣)")
        st.write("賣出交易稅: 0.1%")
        st.write(f"分析期間: 近{years}年")
        st.write(f"平均回報率: {avg_return:.2%}")
        st.write(f"分析的除息事件數量: {event_count}")
        
        st.subheader('詳細回報率:')
        df = pd.DataFrame(detailed_returns, columns=['除息日', '回報率'])
        df['除息日'] = df['除息日'].dt.strftime('%Y-%m-%d')
        df['回報率'] = df['回報率'].apply(lambda x: f"{x:.2%}")
        st.dataframe(df)
