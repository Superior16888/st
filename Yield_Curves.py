import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime, timedelta

# Function to fetch yield data from Yahoo Finance
def fetch_yield_data(start_date, end_date):
    tickers = ['^IRX', '^FVX', '^TNX', '^TYX']  # 3-month, 5-year, 10-year, 30-year yields
    yields = yf.download(tickers, start=start_date, end=end_date)['Adj Close']
    desired_order = ['^IRX', '^FVX', '^TNX', '^TYX']
    return yields[desired_order]

# Function to create the yield curve plot
def create_yield_curve_plot(yields, days_ago):
    maturities = ['3M', '5Y', '10Y', '30Y']
    current_yields = yields.iloc[-1].values
    yields_n_days_ago = yields.iloc[-days_ago-1].values if len(yields) > days_ago else yields.iloc[0].values

    fig = go.Figure()

    # Plot for today's yields
    fig.add_trace(go.Scatter(x=maturities, y=current_yields, mode='lines+markers', name='Today',
                             line=dict(color='blue', width=2), marker=dict(size=8)))
    
    # Plot for yields 'days_ago' days ago
    fig.add_trace(go.Scatter(x=maturities, y=yields_n_days_ago, mode='lines+markers', name=f'{days_ago} Days Ago',
                             line=dict(color='orange', width=2, dash='dash'), marker=dict(size=8)))

    # Update layout: x-axis labels, y-axis starting from 0
    fig.update_layout(
        title=f'美債殖利率: 今天 vs {days_ago} 交易日前',
        xaxis_title='年期',
        yaxis_title='殖利率 (%)',
        xaxis=dict(type='category'),
        yaxis=dict(range=[0, None]),  # Start y-axis from 0
        legend=dict(
            x=0.75,
            y=0.95,
            bgcolor='rgba(255, 255, 255, 0.5)',
            bordercolor='black',
            borderwidth=1
        ),
        width=800,
        height=500
    )

    return fig

# Streamlit app starts here
st.title('美債殖利率變動')

# Automatically set the date range for the past year
end_date = datetime.now()
start_date = end_date - timedelta(days=365*3)

# Fetch the yield data
yields = fetch_yield_data(start_date, end_date)

# Calculate the difference in days between the first and last date
days_difference = (yields.index[-1] - yields.index[0]).days

# Number of days ago selection, with the maximum value capped by the data range
days_ago = st.slider("距今日之交易日數", min_value=1, max_value=min(days_difference, 750), value=2)

# Create and display the yield curve plot
if not yields.empty:
    fig = create_yield_curve_plot(yields, days_ago)
    st.plotly_chart(fig)
    
    # Display the yield data with reversed index
    st.subheader("殖利率 (倒序)")
    st.dataframe(yields.iloc[::-1])  # Reverse the index of the DataFrame
else:
    st.error("無資料.")
