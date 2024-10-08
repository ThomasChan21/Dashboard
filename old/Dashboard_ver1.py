import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from dotenv import load_dotenv
from PIL import Image
import folium
from streamlit_folium import st_folium
import base64

warnings.filterwarnings('ignore')

load_dotenv()

st.set_page_config(page_title="全幢及大手成交Dashboard(測試版)", page_icon=":bar_chart:",layout="wide")

st.title(" :bar_chart: 全幢及大手成交Dashboard(測試版)") 
st.markdown('<style>div.block-container{padding-top:3rem;}</style>',unsafe_allow_html=True)


#loading data

fl = st.file_uploader(":file_folder: 上載檔案",type=(["csv"]))
if fl is not None:
    filename = fl.name
    st.write(filename)
    df = pd.read_csv(filename)
else:
    os.chdir(r"C:\Users\icisuser\GIS\Dashboard\Dashboard_vsc")
    df = pd.read_csv("2024wbtxns43.csv")

df = df[["資料日期","物業地址","全幢or非全幢","地盤面積","成交價","成交價(億港元)","現樓面面積","現樓面呎價","可建樓面面積","重建呎價","照片", "分類","入伙日期","房間數目及每間售價","賣家","買家","資料來源","新聞連結","備註","Date","地區_18區","longitude_lands","latitude_lands"]].copy() 

# Replace NaN values with a placeholder (e.g., 'N/A')
df = df.fillna('N/A')

# Add popup content column with clickable link to the dataframe

#path_to_images = r"C:\Users\icisuser\GIS\Dashboard\Dashboard_vsc\images"




# Define image handling functions
@st.cache_data
def get_image_path(filename):
    full_path = os.path.join(r"C:\Users\icisuser\GIS\Dashboard\Dashboard_vsc\images", filename[-12:])
    #print(full_path)
    return full_path if os.path.exists(full_path) else None

@st.cache_data
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ''

# Generate popups with image encoding
def generate_popups(df):
    popups = []
    for _, row in df.iterrows():
        img_path = get_image_path(row['照片'])

        # Check if the img_path is valid before processing
        if img_path:
            encoded_image = get_image_base64(img_path)
        else:
            encoded_image = ''  # No image found, set to empty or placeholder
        
        # Use a placeholder if the image is not found
        image_html = f'<img src="data:image/jpeg;base64,{encoded_image}" width="200">' if encoded_image else 'Image not found'

        popups.append(f"""
            <b>物業地址 :</b> {row['物業地址']}<br>
            <b>成交價 :</b> {row['成交價']}<br>
            <b>地盤面積 :</b> {row['地盤面積']}<br>
            <b>現樓面面積 :</b> {row['現樓面面積']}<br>
            <b>現樓面呎價 :</b> {row['現樓面呎價']}<br>
            <b>可建樓面面積 :</b> {row['可建樓面面積']}<br>
            <b>重建呎價 :</b> {row['重建呎價']}<br>
            <b>照片 :</b> {image_html}><br>
            <b>分類 :</b> {row['分類']}<br>
            <b>全幢或非全幢 :</b> {row['全幢or非全幢']}<br>
            <b>入伙日期 :</b> {row['入伙日期']}<br>
            <b>房間數目及每間售價 :</b> {row['房間數目及每間售價']}<br>
            <b>賣家 :</b> {row['賣家']}<br>
            <b>買家 :</b> {row['買家']}<br>
            <b>資料來源 :</b> {row['資料來源']}<br>
            <b>新聞連結 :</b> <a href="{row['新聞連結']}" target="_blank">Click here</a><br>
            <b>資料日期 :</b> {row['資料日期']}<br>
            <b>備註 :</b> {row['備註']}<br>
        """)
    return popups

# Generate popups and add to DataFrame
df["Popup"] = generate_popups(df)


# Convert all columns to strings (becasue of Serialization of dataframe to Arrow table)
df = df.astype(str)

#st.write(df["Popup"].head())   

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


# Create a Map
# 顯示地圖，將台北市各區域標記在地圖上，大小和顏色表示人口數

# filtered_df.rename(columns={"latitude_lands": "lat"}, inplace=True)
# filtered_df.rename(columns={"longitude_lands": "lon"}, inplace=True)

# st.map(data = filtered_df, #size = filtered_df["成交價(億港元)"]
#     # color = filtered_df["成交價(億港元)"]
#     size = 6,
#     use_container_width=True
# )

# Create a Folium map

map = folium.Map(
    location=[22.39,114.14], 
    zoom_start=11, 
    min_zoom=11, 
    max_zoom=20,
    control_scale=True)

folium.TileLayer(
    tiles="https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/basemap/WGS84/{z}/{x}/{y}.png",
    attr="<a href='https://api.portal.hkmapservice.gov.hk/disclaimer' target='_blank' class='copyrightDiv'>&copy; 地圖資料由地政總署提供</a><div style='width:28px;height:28px;display:inline-flex;background:url(https://api.hkmapservice.gov.hk/mapapi/landsdlogo.jpg);background-size:28px;'></div> ",
    name="Topographical Map",
    max_native_zoom=20
).add_to(map)

folium.TileLayer(
    tiles="https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/label/hk/tc/WGS84/{z}/{x}/{y}.png",
    attr="Lands Department",
    name="Lands Department",
    max_native_zoom=20,
    overlay=True
).add_to(map)

folium.LayerControl().add_to(map)


print(df.dtypes)


# Add markers to the map
@st.cache_data
def set_icon(bldg_type):
    if bldg_type == '車位或停車場大廈':
        return ('lightgreen', 'car')
    elif bldg_type == '工業':
        return ('orange','industry')
    elif bldg_type == '商業':
        return ('red','building')
    elif bldg_type == '酒店':
        return ('darkblue','bed')
    elif bldg_type == '商場或商鋪或基座商鋪':
        return ('blue','shopping-bag')
    elif bldg_type == '地盤（包括強拍）':
        return ('beige','location-arrow')
    elif bldg_type == '住宅':
        return ('lightred','home')
    elif bldg_type == '商住':
        return ('purple','television')
    elif bldg_type == '其他（包括學校、戲院、農地等）':
        return ('green','map')
    else:
        return ('lightgray','battery-quarter')

def display_marker():
    for _, row in filtered_df.iterrows():
        icon_color, icon_name = set_icon(row['分類'])

        markers = folium.Marker(
            location=[float(row['latitude_lands']), float(row['longitude_lands'])],
            popup=folium.Popup(row['Popup'], max_width=250),
            icon=folium.Icon(color=icon_color, icon_color='white', icon=icon_name, prefix='fa') 
        ).add_to(map)

display_marker()


print(filtered_df["Popup"])

st_map = st_folium(map, width="75%", height=650) 

column1, column2 = st.columns((2))

with column1:
    st.subheader("全幢及大手成交(宗數，按物業類型)")
    fig = px.bar(type_df_indexed, x = "分類", y = "成交宗數", text = ['{:.0f}宗'.format(x) for x in type_df_indexed["成交宗數"]], color="分類", template = "seaborn")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True, height = 200)

with column2:
    st.subheader("全幢及大手成交(金額比例，按物業類型)")
    fig = px.pie(filtered_df, values = "成交價(億港元)", names = "分類", hole = 0.5)
    fig.update_traces(text = filtered_df["分類"], textposition = "outside")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig,use_container_width=True)
 
# Metric for 10 class of Properties

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
        


 
print("\n")


# Create Time Series Analysis  
filtered_df["month_year"] = filtered_df["Date"].dt.to_period("M")
st.subheader('時間序列分析')

# Convert '成交價(億港元)' to float (added this line)
filtered_df['成交價(億港元)'] = filtered_df['成交價(億港元)'].astype(float)

# Group by 'month_year' and sum '成交價(億港元)'
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["成交價(億港元)"].sum()).reset_index()
fig2 = px.line(linechart, x = "month_year", y="成交價(億港元)", labels = {"month_year": "月份"},height=500, width = 1000,template="gridon")
st.plotly_chart(fig2,use_container_width=True)

with st.expander("View Data of TimeSeries:"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data = csv, file_name = "TimeSeries.csv", mime ='text/csv')  
    
    
    
    
    
    
    
    