import streamlit as st
import numpy as np
import pandas as pd
import datetime
import warnings
warnings.filterwarnings("ignore")

# Set page title
st.set_page_config(page_title="主要壽險公司 IFRS 9 資產佔比")

# Title
st.title("主要壽險公司 IFRS 9 資產佔比")

# Define insurance companies and their IDs
Name = ['新光人壽', '國泰人壽', '南山人壽', '富邦人壽', '台灣人壽', '中國人壽', '全球人壽']
ID = ['03458902','03374707','11456006','27935073','03557017','03434016','70817744']
insurance_dict = dict(zip(Name, ID))

# Function to fetch and process data
@st.cache_data
def fetch_and_process_data():
    data = pd.read_html(f'https://ins-info.ib.gov.tw/customer/Info2-2.aspx?UID={ID[0]}', 
                        encoding='utf-8')[1].iloc[[5,10,7,20],[2,3,4,5]]
    data.set_index('項目', inplace=True)
    data = (data/100000).astype(int)
    Period = data.columns[0]
    
    佔總資產比 = []
    金融資產佔比 = []
    
    for i in range(len(ID)):
        IFRS9_Ratio = pd.read_html(f'https://ins-info.ib.gov.tw/customer/Info2-2.aspx?UID={ID[i]}', encoding='utf-8')[1]
        IFRS9_Ratio = IFRS9_Ratio.iloc[[5,10,7,20]][['項目',Period]]
        IFRS9_Ratio['佔比'] = [round(IFRS9_Ratio.iloc[i][Period]/IFRS9_Ratio.iloc[-1][Period], 2) for i in range(len(IFRS9_Ratio))]
        佔總資產比.append(list(IFRS9_Ratio['佔比']))
        
        sum_of_first_three = sum(佔總資產比[-1][:3])
        individual_金融資產佔比 = [x / sum_of_first_three for x in 佔總資產比[-1][:3]]
        金融資產佔比.append(individual_金融資產佔比)
    
    佔總資產比_df = pd.DataFrame(佔總資產比, index=insurance_dict.keys(), columns=["FVPL_PLO", "FVOCI","AC","總資產"])
    佔總資產比_df['金融資產'] = 佔總資產比_df['FVPL_PLO'] + 佔總資產比_df['FVOCI'] + 佔總資產比_df['AC']
    
    return 佔總資產比_df, Period

# Fetch and process data
df, period = fetch_and_process_data()

# Display the period
st.write(f"資料日期: {period}")

# Create a bar chart
st.write("IFRS 9 分類資產佔總資產比例")
chart_data = df[['FVPL_PLO', 'FVOCI', 'AC']]
st.bar_chart(chart_data)

# Display the dataframe
#st.write("IFRS 9 分類資產佔總資產比例")
st.dataframe(df.style.format("{:.0%}"))

# Add some explanations
st.write("""
資料來源：自動抓取最新保險業資訊公開網站整理。https://ins-info.ib.gov.tw/customer/announceinfo.aspx
- FVPL_PLO: Fair Value through Profit or Loss
- FVOCI: Fair Value through Other Comprehensive Income
- AC: Amortized Cost
""")

# You can add more visualizations or analysis here as needed
