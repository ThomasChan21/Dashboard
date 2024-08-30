import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from dotenv import load_dotenv
from PIL import Image
warnings.filterwarnings('ignore')

load_dotenv()

st.set_page_config(page_title="全幢及大手成交Dashboard(測試版)", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: 全幢及大手成交Dashboard(測試版)") 
st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)

@st.cache_data
def load_data(file):
    data = pd.read_csv(file, encoding = "utf-8")
    return data

fl = st.file_uploader(":file_folder: 上載檔案",type=(["csv"]))
if fl is None:
    st.info("請上載 csv 檔案", icon="ℹ️")
    st.stop()

loaded_df = load_data(fl)
df = loaded_df[["資料日期","物業地址","全幢or非全幢","地盤面積","成交價","成交價(億港元)","現樓面面積","現樓面呎價","可建樓面面積","重建呎價","分類","入伙日期","房間數目及每間售價","賣家","買家","資料來源","新聞連結","備註","Date","地區_18區","longitude_lands","latitude_lands"]].copy() 

# create Iamge for 10 types of Properties
c1, c2, c3, c4, c5, c6, c7, c8, c9, c10 = st.columns((10))

col1, col2 = st.columns((2))
df["Date"] = pd.to_datetime(df["Date"])

# Getting the min and max date 
startDate = pd.to_datetime(df["Date"]).min()
endDate = pd.to_datetime(df["Date"]).max()

with col1:
    date1 = pd.to_datetime(st.date_input("開始日期", startDate))

with col2:
    date2 = pd.to_datetime(st.date_input("結束日期", endDate))

df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()

st.sidebar.header("選擇篩選類別: ")

# Create for Date (to be followed)

#with st.sidebar:
#    date1 = pd.to_datetime(st.date_input("開始日期", startDate))
#    date2 = pd.to_datetime(st.date_input("結束日期", endDate))

#    df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()


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
wb = st.sidebar.multiselect("選擇全幢或非全幢",df3["全幢or非全幢"].unique())

# Filter the data based on 地區, 物業類型 and 全幢或非全幢

if not district and not building_type and not wb:
    filtered_df = df
elif not building_type and not wb:
    filtered_df = df[df["地區_18區"].isin(district)]
elif not district and not wb:
    filtered_df = df[df["分類"].isin(building_type)]
elif building_type and wb:
    filtered_df = df3[df["分類"].isin(building_type) & df3["全幢or非全幢"].isin(wb)]
elif district and wb:
    filtered_df = df3[df["地區_18區"].isin(district) & df3["全幢or非全幢"].isin(wb)]
elif district and building_type:
    filtered_df = df3[df["地區_18區"].isin(district) & df3["分類"].isin(building_type)]
elif wb:
    filtered_df = df3[df3["全幢or非全幢"].isin(wb)]
else:
    filtered_df = df3[df3["地區_18區"].isin(district) & df3["分類"].isin(building_type) & df3["全幢or非全幢"].isin(wb)]

type_df = filtered_df.groupby(by = ["分類"], as_index = False)["成交價(億港元)"].count()
type_df.rename(columns={"成交價(億港元)": "成交宗數"}, inplace=True)
type_df["newIndex"] = type_df["分類"]
# print(type_df)"
type_df_indexed = type_df.sort_values(by="成交宗數", ascending=False).set_index("newIndex")
# print(type_df)

with col1:
    st.subheader("全幢及大手成交(宗數，按物業類型)")
    fig = px.bar(type_df_indexed, x = "分類", y = "成交宗數", text = ['{:.0f}宗'.format(x) for x in type_df_indexed["成交宗數"]], color="分類", template = "seaborn")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True, height = 200)

with col2:
    st.subheader("全幢及大手成交(金額比例，按物業類型)")
    fig = px.pie(filtered_df, values = "成交價(億港元)", names = "分類", hole = 0.5)
    fig.update_traces(text = filtered_df["分類"], textposition = "outside")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
 
# Metric for 10 class of Properties
print(type_df) # test what is inside this df
print("=======================")
print(type_df_indexed) # test what is inside this df
print("=======================")
#print(type_df_indexed.loc["住宅","成交宗數"])

with c1:
    image01 = Image.open('./classphoto/住宅.jpg')
    st.image(image01, caption="住宅")
    if type_df_indexed["分類"].isin(["住宅"]).any():
        st.metric(label="住宅成交宗數", value=type_df_indexed.loc["住宅","成交宗數"])
    else:
        st.metric(label="住宅成交宗數", value=0)
with c6:
    image02 = Image.open('./classphoto/工業.jpg')
    st.image(image02, caption="工業")
    if type_df_indexed["分類"].isin(["工業"]).any():
        st.metric(label="工業成交宗數", value=type_df_indexed.loc["工業","成交宗數"])
    else:
        st.metric(label="工業成交宗數", value=0)
with c2:
    image03 = Image.open('./classphoto/商業.jpg')
    st.image(image03, caption="商業")
    if type_df_indexed["分類"].isin(["商業"]).any():
        st.metric(label="商業成交宗數", value=type_df_indexed.loc["商業","成交宗數"])
    else:
        st.metric(label="商業成交宗數", value=0)
with c4:
    image04 = Image.open('./classphoto/商場.jpg')
    st.image(image04, caption="商舖/商場")
    if type_df_indexed["分類"].isin(["商場或商鋪或基座商鋪"]).any():
        st.metric(label="商舖/商場成交宗數", value=type_df_indexed.loc["商場或商鋪或基座商鋪","成交宗數"])
    else:
        st.metric(label="商舖/商場成交宗數", value=0)

with c5:
    image05 = Image.open('./classphoto/舊樓.jpg')
    st.image(image05, caption="舊樓")
    if type_df_indexed["分類"].isin(["1960年及之前入伙舊樓"]).any():
        st.metric(label="舊樓成交宗數", value=type_df_indexed.loc["1960年及之前入伙舊樓","成交宗數"])
    else:
        st.metric(label="舊樓成交宗數", value=0)
with c8:
    image06 = Image.open('./classphoto/酒店.jpg')
    st.image(image06, caption="酒店")
    if type_df_indexed["分類"].isin(["酒店"]).any():
        st.metric(label="酒店成交宗數", value=type_df_indexed.loc["酒店","成交宗數"])
    else:
        st.metric(label="酒店成交宗數", value=0)
with c9:
    image07 = Image.open('./classphoto/車位.jpg')
    st.image(image07, caption="車位")
    if type_df_indexed["分類"].isin(["車位或停車場大廈"]).any():
        st.metric(label="車位成交宗數", value=type_df_indexed.loc["車位或停車場大廈","成交宗數"])
    else:
        st.metric(label="車位成交宗數", value=0)
with c3:
    image08 = Image.open('./classphoto/地盤.jpg')
    st.image(image08, caption="地盤")
    if type_df_indexed["分類"].isin(["地盤（包括強拍）"]).any():
        st.metric(label="地盤成交宗數", value=type_df_indexed.loc["地盤（包括強拍）","成交宗數"])
    else:
        st.metric(label="地盤成交宗數", value=0)
with c7:
    image09 = Image.open('./classphoto/商住.jpg')
    st.image(image09, caption="商住")
    if type_df_indexed["分類"].isin(["商住"]).any():
        st.metric(label="商住成交宗數", value=type_df_indexed.loc["商住","成交宗數"])
    else:
        st.metric(label="商住成交宗數", value=0)
with c10:
    image10 = Image.open('./classphoto/其他.jpg')
    st.image(image10, caption="其他")
    if type_df_indexed["分類"].isin(["其他（包括學校、戲院、農地等）"]).any():
        st.metric(label="其他成交宗數", value=type_df_indexed.loc["其他（包括學校、戲院、農地等）","成交宗數"])
    else:
        st.metric(label="其他成交宗數", value=0)

# view Data
    
with st.expander("篩選資料 - viewData"):
    # region = filtered_df.groupby(by = "Region", as_index = False)["Sales"].sum()
    st.dataframe(filtered_df.style.background_gradient(cmap="Oranges"), 
                 column_order=("資料日期","地區_18區","物業地址","全幢or非全幢","地盤面積","成交價(億港元)","現樓面面積","現樓面呎價","可建樓面面積","重建呎價","分類","入伙日期","照片","房間數目及每間售價","賣家","買家","資料來源","新聞連結","備註"),
                 column_config={
                     "資料日期": st.column_config.DateColumn(
                         "資料日期",
                         format="YYYY.MM.DD",
                     ), # Note: column "資料日期" cannot be used because it enclose time element which is added fr above min and max --> see line 35 and 36
                     "新聞連結": st.column_config.LinkColumn(
                        validate=r"^https://[a-z]+\.streamlit\.app$",
                        max_chars=150,
                        display_text=r"https://(.*?)\.streamlit\.app"
                     ),
                     "地區_18區": st.column_config.TextColumn(
                         "地區"
                     ),
                    "全幢or非全幢": st.column_config.TextColumn(
                         "全幢或非全幢"
                     )
                 })
    # st.write(filtered_df.style.background_gradient(cmap="Oranges"))
    csv = filtered_df.to_csv(index = False, encoding='utf-8')
    st.download_button("Download Data", data = csv, file_name = "篩選資料_成交記錄.csv", mime = "text/csv", help = 'Click here to download the data as a CSV file')
        

# Create a Map
# 顯示地圖，將台北市各區域標記在地圖上，大小和顏色表示人口數

filtered_df.rename(columns={"latitude_lands": "lat"}, inplace=True)
filtered_df.rename(columns={"longitude_lands": "lon"}, inplace=True)

st.map(data = filtered_df, #size = filtered_df["成交價(億港元)"]
    # color = filtered_df["成交價(億港元)"]
    size = 6,
    use_container_width=True
)
 
print("\n")


# Create Time Series Analysis  
filtered_df["month_year"] = filtered_df["Date"].dt.to_period("M")
st.subheader('時間序列分析')

linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["成交價(億港元)"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="成交價(億港元)", labels = {"month_year": "月份"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')  
    
    
    
    
    
    
    
    