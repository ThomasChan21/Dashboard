import streamlit as st
import urllib.request as request
import json
import pandas as pd
import plotly.express as px


st.set_page_config(page_title="經濟環境", page_icon=":bar_chart:",layout="wide")
st.title("經濟環境")

# 1. Gross Domestic Product
src = "https://www.censtatd.gov.hk/api/get.php?id=310-31001&lang=en&param=N4KABGBEDGBukC4zAL4BpxQM7yaCEkAwgPIByiYA2pgVAEoCGA7gPoCyrAFgNYAmrPpAx1CATQD2Y1gEY+AB1YBSVlki0wAXREFIAZQCCMyjVFQAihPOyFy1erqbM6TJHkBTAE4BLCULwakFgALoyewZSQAEwADDIAHHEOYC6E3v5QAMwyMQC02TFJOpAANowAdgDmke7l6ihAA"

with request.urlopen(src) as response:
    data=json.load(response)

data = data["dataSet"]
df = pd.DataFrame(data)
#print(df)
#st.write(df)

#select GPD quarterly change column

df_yr = df[(df["freq"]=="Q") & (df["sv"] == "CON") & (df["svDesc"] == "Year-on-year % change") ]
#df_qr = df[(df["freq"]=="Q") & (df["sv"] == "CON") & (df["svDesc"] == "Quarter-to-quarter % change") ]
#st.write(df)



col1, col2 = st.columns((2))

with col1:
    st.subheader("本地生產總值-按年變動百分率 (2018-2024 Q2)")
    fig = px.bar(df_yr, x="period", y="figure", template="seaborn")
    fig.update_layout(xaxis_title="period", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, height=200)

