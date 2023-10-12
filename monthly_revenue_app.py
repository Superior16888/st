import streamlit as st
import requests
import io
import pandas as pd
import numpy as np
import plotly.express as px

st.title("Monthly Revenue Analysis")

# Input for year and month
year = st.slider("Select Year", 100, 121, 112)
month = st.slider("Select Month", 1, 12, 7)

def monthly_revenue(year, month):
    url = "https://mops.twse.com.tw/server-java/FileDownLoad" 
    payload = {
        "step": "9",
        "functionName": "show_file2",
        "filePath": "/t21/sii/",
        "fileName": f"t21sc03_{year}_{month}.csv"
    }
    response = requests.post(url, data=payload)
    response.encoding = 'utf-8'
    df = pd.read_csv(io.StringIO(response.text))
    
    # Data processing
    df['公司名稱'] = df['公司名稱'] + "<br>" + df['公司代號'].astype(str)
    df_filtered = df[df['營業收入-當月營收'] > 0]
    df_filtered = df_filtered[['產業別','公司名稱','營業收入-當月營收','營業收入-上月營收','累計營業收入-當月累計營收','累計營業收入-去年累計營收']]
    df_filtered['營業收入-當月營收'] = (df_filtered['營業收入-當月營收'] / 100000)
    df_filtered['營業收入-上月營收'] = df_filtered['營業收入-上月營收'] / 100000
    df_filtered['月營收增減'] = (df_filtered['營業收入-當月營收'] - df_filtered['營業收入-上月營收']) / df_filtered['營業收入-上月營收'].abs()
    df_filtered['累計營業收入-當月累計營收'] = df_filtered['累計營業收入-當月累計營收'] / 100000
    df_filtered['累計營業收入-去年累計營收'] = df_filtered['累計營業收入-去年累計營收'] / 100000
    df_filtered['累計營收增減'] = (df_filtered['累計營業收入-當月累計營收'] - df_filtered['累計營業收入-去年累計營收']) / df_filtered['累計營業收入-去年累計營收'].abs()
    return df_filtered

df_filtered = monthly_revenue(year, month)

# Create the treemap visualization
limit = 0.5
df_filtered['color'] = np.where(df_filtered['月營收增減'] > limit, limit, 
              np.where(df_filtered['月營收增減'] < -limit, -limit, df_filtered['月營收增減']))
fig = px.treemap(df_filtered, 
                 path=[px.Constant('月營收'),'產業別','公司名稱'],
                 values='營業收入-當月營收',
                 color='color',
                 color_continuous_scale='RdYlBu_r',
                 width=1200, height=700,
                 color_continuous_midpoint=0,
                 custom_data=['累計營收增減','累計營業收入-當月累計營收','累計營業收入-去年累計營收']) 

fig.update_layout(margin=dict(t=30, l=10, r=10, b=5))
fig.update_traces(hovertemplate='當月營收(億)：%{value:.0f}<br>營收變動: %{color:.1%}<br>當年累計營收: %{customdata[1]:.0f}<br>累計營收變動: %{customdata[0]:.1%}')
fig.update_traces(textinfo='label+percent entry')
fig.update_traces(textfont_size=16)

# Display the Plotly treemap
st.plotly_chart(fig)
