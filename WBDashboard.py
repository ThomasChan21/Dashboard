import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from dotenv import load_dotenv
warnings.filterwarnings('ignore')

load_dotenv()

st.set_page_config(page_title="全幢及大手成交Dashboard", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: 全幢及大手成交") 
st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)

fl = st.file_uploader(":file_folder: 上載檔案",type=(["csv","txt","xlsx","xls"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename, encoding = "utf-8")
else:
    os.chdir(r"C:\Users\icisuser\GIS\Dashboard\Dashboard_vsc")
    df = pd.read_csv("2024wbtxn43s.csv", encoding = "utf-8")

col1, col2 = st.columns((2))
df["資料日期"] = pd.to_datetime(df["資料日期"])

# Getting the min and max date 
startDate = pd.to_datetime(df["資料日期"]).min()
endDate = pd.to_datetime(df["資料日期"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("開始日期", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("結束日期", endDate))

df = df[(df["資料日期"] >= date1) & (df["資料日期"] <= date2)].copy()

st.sidebar.header("選擇篩選類別: ")
# Create for 地區
district = st.sidebar.multiselect("選擇地區", df["地區_18區"].unique())
if not district:
    df2 = df.copy()
else:
    df2 = df[df["地區_18區"].isin(district)]

# Create for 物業類型
building_type = st.sidebar.multiselect("選擇物業類型", df2["分類"].unique())
if not building_type:
    df3 = df2.copy()
else:
    df3 = df2[df2["分類"].isin(building_type)]

# Create for 全幢或大手
wb = st.sidebar.multiselect("選擇全幢或大手",df3["全幢or大手"].unique())

# Filter the data based on 地區, 物業類型 and 全幢或大手

if not district and not building_type and not wb:
    filtered_df = df
elif not building_type and not wb:
    filtered_df = df[df["地區_18區"].isin(district)]
elif not district and not wb:
    filtered_df = df[df["分類"].isin(building_type)]
elif building_type and wb:
    filtered_df = df3[df["分類"].isin(building_type) & df3["全幢or大手"].isin(wb)]
elif district and wb:
    filtered_df = df3[df["地區_18區"].isin(district) & df3["全幢or大手"].isin(wb)]
elif district and building_type:
    filtered_df = df3[df["地區_18區"].isin(district) & df3["分類"].isin(building_type)]
elif wb:
    filtered_df = df3[df3["全幢or大手"].isin(wb)]
else:
    filtered_df = df3[df3["地區_18區"].isin(district) & df3["分類"].isin(building_type) & df3["全幢or大手"].isin(wb)]

type_df = filtered_df.groupby(by = ["分類"], as_index = False)["成交價(億港元)"].count()
type_df.rename(columns={"成交價(億港元)": "成交宗數"}, inplace=True)
# print(type_df)

with col1:
    st.subheader("全幢及大手成交(宗數，按物業類型)")
    fig = px.bar(type_df, x = "分類", y = "成交宗數", text = ['{:.0f}宗'.format(x) for x in type_df["成交宗數"]], color="分類", template = "seaborn")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("全幢及大手成交(金額比例，按物業類型)")
    fig = px.pie(filtered_df, values = "成交價(億港元)", names = "分類", hole = 0.5)
    fig.update_traces(text = filtered_df["分類"], textposition = "outside")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
 
# print(filtered_df["成交價(億港元)"],'\n', filtered_df["成交價"])
# print(year_df["成交宗數"])

# view Data

cl1, cl2 = st.columns((2))
with cl1:
    with st.expander("成交資料 (宗數) - viewData"):
        st.write(type_df.style.background_gradient(cmap="Blues"))
        csv = type_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "成交資料_宗數.csv", mime = "text/csv",
                            help = 'Click here to download the data as a CSV file')

with cl2:
    with st.expander("成交資料 (金額比例) - viewData"):
        # region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
        st.write(filtered_df.style.background_gradient(cmap="Oranges"))
        csv = filtered_df.to_csv(index = False).encode('utf-8')
        st.download_button("Download Data", data = csv, file_name = "成交資料_金額.csv", mime = "text/csv",
                        help = 'Click here to download the data as a CSV file')
        
# filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
# st.subheader('Time Series Analysis')
    
# Create a Map
# 顯示地圖，將台北市各區域標記在地圖上，大小和顏色表示人口數

filtered_df.rename(columns={"latitude_lands": "lat"}, inplace=True)
filtered_df.rename(columns={"longitude_lands": "lon"}, inplace=True)

st.map(data = filtered_df, #size = filtered_df["成交價(億港元)"]
    # color = filtered_df["成交價(億港元)"]
    size = 5,
    use_container_width=True
)
 
# st.map(df_boundaries,
#     latitude='南緯度',
#     longitude='西經度', size=100, color='#0044ff')
     
print(filtered_df)   

# Create Time Series Analysis  
filtered_df["month_year"] = filtered_df["資料日期"].dt.to_period("M")
st.subheader('時間序列分析')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["成交價(億港元)"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="成交價(億港元)", labels = {"month_year": "月份"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')  
    
    
    
    
    
    
    
    