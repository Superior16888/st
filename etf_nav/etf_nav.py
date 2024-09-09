import streamlit as st
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time
import re
import plotly.express as px
import numpy as np

def scrape_etf_data(url):
    options = uc.ChromeOptions()
    options.add_argument("--headless")
    
    driver = uc.Chrome(options=options)
    
    driver.get(url)
    wait = WebDriverWait(driver, 10)
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.title")))
    time.sleep(5)  # Additional wait for dynamic content
    titles = driver.find_elements(By.CSS_SELECTOR, "div.title")
    title_texts = [title.text.strip() for title in titles]     
    tables = driver.find_elements(By.CSS_SELECTOR, "table.table")   
    all_data = []    
    for i, table in enumerate(tables):
        title = title_texts[i] if i < len(title_texts) else "未分類"
        headers = ['分類'] + [th.text.strip() for th in table.find_elements(By.TAG_NAME, "th")]   
        rows = table.find_elements(By.TAG_NAME, "tr")[1:]  # Skip header row
        data = []
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [title] + [cell.text.strip() for cell in cells]
            if len(row_data) == len(headers):
                data.append(row_data)
        
        df = pd.DataFrame(data, columns=headers)
        all_data.append(df)
    
    final_df = pd.concat(all_data, ignore_index=True)
    driver.quit()
    return final_df

def load_data():
    urls = [
        "https://mis.twse.com.tw/stock/various-areas/etf-price/indicator-disclosure-etf?lang=zhHant",
        "https://mis.twse.com.tw/stock/various-areas/etf-price/value-disclosure-etf?lang=zhHant"
    ]

    ETF_data = pd.DataFrame()
    for url in urls:
        df = scrape_etf_data(url)
        if not df.empty:
            df['交易所'] = 'TSE' if "indicator-disclosure-etf" in url else 'OTC'
            ETF_data = pd.concat([ETF_data, df], ignore_index=True)
        else:
            st.error(f"No data retrieved from {url}")

    if 'ETF代號/名稱' in ETF_data.columns:
        ETF_data[['ETF代號', 'ETF名稱']] = ETF_data['ETF代號/名稱'].str.split('/', expand=True)
        ETF_data['ETF代號'] = ETF_data['ETF代號'].str.strip()
        ETF_data['ETF名稱'] = ETF_data['ETF名稱'].str.strip()
        ETF_data = ETF_data.drop('ETF代號/名稱', axis=1)
    else:
        st.error("Column 'ETF代號/名稱' not found in the DataFrame")

    ETF_data.columns = [re.sub(r'\([^()]*\)', '', col).replace('\n', '').strip() for col in ETF_data.columns]

    ETF_data['yf_ticker'] = ETF_data.apply(lambda row: row['ETF代號'] + '.TW' if row['交易所'] == 'TSE' else row['ETF代號'] + '.TWO', axis=1)
    ETF_data['已發行受益權單位數'] = ETF_data['已發行受益權單位數'].str.replace(',', '').astype(float)
    ETF_data['與前日已發行受益單位差異數'] = ETF_data['與前日已發行受益單位差異數'].str.replace(',', '').astype(float)
    ETF_data['成交價'] = ETF_data['成交價'].str.replace(',', '').astype(float)
    ETF_data['投信或總代理人預估淨值'] = ETF_data['投信或總代理人預估淨值'].str.replace(',', '').astype(float)
    ETF_data['預估折溢價幅度'] = ETF_data['預估折溢價幅度'].apply(lambda x: float(x.rstrip('%')) if x != '-' else 0)
    ETF_data['前一營業日單位淨值'] = pd.to_numeric(ETF_data['前一營業日單位淨值'].str.replace('未結出', '').str.replace(',', ''), errors='coerce')
    ETF_data['ETF市值'] = ETF_data['已發行受益權單位數'] * ETF_data['成交價']/100000000
    ETF_data['ETF市值'] = ETF_data['ETF市值'].round(2).astype(float)

    asset_type_mapping = {
        'L': '正向槓桿型',
        'R': '反向槓桿型',
        'K': '外幣股票',
        'U': '商品期貨',
        'B': '台幣債券型',
    }
    def map_asset_type(code):
        last_letter = code[-1]
        return asset_type_mapping.get(last_letter, '台幣股票型')
    ETF_data['資產類型'] = ETF_data['ETF代號'].apply(map_asset_type)

    return ETF_data

def create_treemap(df):
    df = df[df['ETF市值'].notna() & (df['ETF市值'] != 0)]
    color = '預估折溢價幅度'
    values = 'ETF市值'

    col_values = df[color]
    weights = df[values]
    weighted_mean = np.average(col_values, weights=weights)
    weighted_std_dev = np.sqrt(np.average((col_values - weighted_mean)**2, weights=weights))

    color_range = max(abs(weighted_mean - 2 * weighted_std_dev), abs(weighted_mean + 2 * weighted_std_dev))
    lower_limit = -color_range
    upper_limit = color_range

    color_scale = [
        (0, "darkgreen"),
        (0.15, "green"),
        (0.5, "white"),
        (0.85, "red"),
        (1, "darkred")
    ]

    data_time = df.iloc[0]['資料時間']
    fig = px.treemap(df, path=[px.Constant(f'ALL_ETF   {data_time}'),'資產類型' ,'ETF代號'], values=values, color=color,
                     color_continuous_scale=color_scale,
                     color_continuous_midpoint = 0,
                     range_color=[lower_limit,upper_limit],
                     hover_data=['ETF代號','ETF名稱','成交價'])
    fig.update_traces(hovertemplate='<b>%{label}</b><br>市值:%{value:,.0f}億<br>%{color:.2f}%')
    fig.data[0].texttemplate = "%{customdata[0]}</br>%{customdata[1]}<br>價:%{customdata[2]:,.1f}"
    fig.data[0]['textfont']['size'] = 12
    fig.update_layout(margin=dict(t=20, l=25, r=20, b=20))
    return fig

def main():
    st.set_page_config(page_title="ETF Data Visualization", layout="wide")
    st.title("ETF 折溢價圖")

    if 'data' not in st.session_state:
        st.session_state.data = None

    if st.button("抓取/更新資料"):
        with st.spinner("Fetching fresh data..."):
            st.session_state.data = load_data()
        st.success("Data fetched successfully!")

    if st.session_state.data is not None:
        fig = create_treemap(st.session_state.data)
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Raw Data")
        st.dataframe(st.session_state.data)
    else:
        st.info("點擊'抓取/更新資料'按鈕更新資料 ")

if __name__ == "__main__":
    main()