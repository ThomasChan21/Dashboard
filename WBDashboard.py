import streamlit as st
import plotly.express as px
import pandas as pd
import os
import warnings
from dotenv import load_dotenv
from PIL import Image
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
import base64
import time

warnings.filterwarnings('ignore')

start_time = time.time()

load_dotenv()

st.set_page_config(page_title="全幢及大手成交Dashboard(測試版)", page_icon=":bar_chart:", layout="wide")

st.title(" :bar_chart: 全幢及大手成交Dashboard(測試版)") 
st.markdown('<style>div.block-container{padding-top:3rem;}</style>', unsafe_allow_html=True)

# Cache the data loading function
@st.cache_data
def load_data(file):
    if file is not None:
        df = pd.read_csv(file)
    else:
        # Use relative path to load the CSV file
        base_dir = os.path.dirname(os.path.abspath(__file__))
        relative_path = os.path.join(base_dir, "2024wbtxns43.csv")
        df = pd.read_csv(relative_path)
    
    df = df[["資料日期","物業地址","全幢or非全幢","地盤面積","成交價","成交價(億港元)","現樓面面積","現樓面呎價","可建樓面面積","重建呎價","照片", "分類","入伙日期","房間數目及每間售價","賣家","買家","資料來源","新聞連結","備註","Date","地區_18區","longitude_lands","latitude_lands"]].copy()
    df = df.fillna('N/A')
    df = df.astype(str)
    return df

# Cache the image path retrieval function
@st.cache_data
def get_image_path(filename):
    # Use relative path to get the image file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    relative_path = os.path.join(base_dir, "images", filename[-12:])
    return relative_path if os.path.exists(relative_path) else None

# Cache the image base64 encoding function
@st.cache_data
def get_image_base64(image_path):
    if os.path.exists(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode()
    return ''

# Generate popups with image encoding
@st.cache_data
def generate_popups(df):
    popups = []
    for _, row in df.iterrows():
        img_path = get_image_path(row['照片'])
        encoded_image = get_image_base64(img_path) if img_path else ''
        image_html = f'<img src="data:image/jpeg;base64,{encoded_image}" width="200">' if encoded_image else 'Image not found'
        popups.append(f"""
        <div style="display: table;">
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">物業地址:</div>
                <div style="display: table-cell;">{row['物業地址']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">成交價:</div>
                <div style="display: table-cell;">{row['成交價']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">地盤面積:</div>
                <div style="display: table-cell;">{row['地盤面積']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">現樓面面積:</div>
                <div style="display: table-cell;">{row['現樓面面積']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">現樓面呎價:</div>
                <div style="display: table-cell;">{row['現樓面呎價']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">可建樓面面積:</div>
                <div style="display: table-cell;">{row['可建樓面面積']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">重建呎價:</div>
                <div style="display: table-cell;">{row['重建呎價']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">照片:</div>
                <div style="display: table-cell;">{image_html}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">分類:</div>
                <div style="display: table-cell;">{row['分類']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">全幢或非全幢:</div>
                <div style="display: table-cell;">{row['全幢or非全幢']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">入伙日期:</div>
                <div style="display: table-cell;">{row['入伙日期']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">房間數目及每間售價:</div>
                <div style="display: table-cell;">{row['房間數目及每間售價']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">賣家:</div>
                <div style="display: table-cell;">{row['賣家']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">買家:</div>
                <div style="display: table-cell;">{row['買家']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">資料來源:</div>
                <div style="display: table-cell;">{row['資料來源']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">新聞連結:</div>
                <div style="display: table-cell;"><a href="{row['新聞連結']}" target="_blank">Click here</a></div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">資料日期:</div>
                <div style="display: table-cell;">{row['資料日期']}</div>
            </div>
            <div style="display: table-row;">
                <div style="display: table-cell; font-weight: bold; white-space: nowrap;">備註:</div>
                <div style="display: table-cell;">{row['備註']}</div>
            </div>
        </div>
        """)
    return popups

# Load data
fl = st.file_uploader(":file_folder: 上載檔案", type=["csv"])
df = load_data(fl)

# Generate popups and add to DataFrame
df["Popup"] = generate_popups(df)

# Create columns for displaying images of 10 types of properties
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

# Cache the filtered data
@st.cache_data
def filter_data(df, date1, date2, district, building_type, wb):
    df = df[(df["Date"] >= date1) & (df["Date"] <= date2)].copy()
    if district:
        df = df[df["地區_18區"].isin(district)]
    if building_type:
        df = df[df["分類"].isin(building_type)]
    if wb:
        df = df[df["全幢or非全幢"].isin(wb)]
    return df

st.sidebar.header("選擇篩選類別: ")

# Create for 地區
district = st.sidebar.multiselect("選擇地區", df["地區_18區"].unique())

# Create for 物業類型
building_type = st.sidebar.multiselect("選擇物業類型", df["分類"].unique())

# Create for 全幢或大手
wb = st.sidebar.multiselect("選擇全幢或非全幢", df["全幢or非全幢"].unique())

# Filter the data
filtered_df = filter_data(df, date1, date2, district, building_type, wb)

type_df = filtered_df.groupby(by=["分類"], as_index=False)["成交價(億港元)"].count()
type_df.rename(columns={"成交價(億港元)": "成交宗數"}, inplace=True)
type_df["newIndex"] = type_df["分類"]
type_df_indexed = type_df.sort_values(by="成交宗數", ascending=False).set_index("newIndex")

# Create a Folium map
map = folium.Map(
    location=[22.39, 114.14], 
    zoom_start=11, 
    min_zoom=11, 
    max_zoom=20,
    control_scale=True
)

# Add Fullscreen control to the map
Fullscreen(position='topright').add_to(map)


# Add tile layers to the map
folium.TileLayer(
    tiles="https://mapapi.geodata.gov.hk/gs/api/v1.0.0/xyz/basemap/WGS84/{z}/{x}/{y}.png",
    attr="<a href='https://api.portal.hkmapservice.gov.hk/disclaimer' target='_blank' class='copyrightDiv'>© 地圖資料由地政總署提供</a><div style='width:28px;height:28px;display:inline-flex;background:url(https://api.hkmapservice.gov.hk/mapapi/landsdlogo.jpg);background-size:28px;'></div>",
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

# Add markers to the map
@st.cache_data
def set_icon(bldg_type):
    icon_dict = {
        '車位或停車場大廈': ('lightgreen', 'car'),
        '工業': ('orange', 'industry'),
        '商業': ('red', 'building'),
        '酒店': ('darkblue', 'bed'),
        '商場或商鋪或基座商鋪': ('blue', 'shopping-bag'),
        '地盤（包括強拍）': ('beige', 'location-arrow'),
        '住宅': ('lightred', 'home'),
        '商住': ('purple', 'television'),
        '其他（包括學校、戲院、農地等）': ('green', 'map')
    }
    return icon_dict.get(bldg_type, ('lightgray', 'battery-quarter'))

def display_marker():
    for _, row in filtered_df.iterrows():
        icon_color, icon_name = set_icon(row['分類'])
        folium.Marker(
            location=[float(row['latitude_lands']), float(row['longitude_lands'])],
            popup=folium.Popup(row['Popup'], max_width=320),
            lazy=False,
            icon=folium.Icon(color=icon_color, icon_color='white', icon=icon_name, prefix='fa')
        ).add_to(map)

display_marker()

# Display the map in Streamlit
st_map = st_folium(map, width="100%", height=650) 

# plot two charts 
column1, column2 = st.columns((2))

with column1:
    st.subheader("全幢及大手成交(宗數，按物業類型)")
    fig = px.bar(type_df_indexed, x="分類", y="成交宗數", text=[f'{x:.0f}宗' for x in type_df_indexed["成交宗數"]], color="分類", template="seaborn")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig, use_container_width=True, height=200)

with column2:
    st.subheader("全幢及大手成交(金額比例，按物業類型)")
    fig = px.pie(filtered_df, values="成交價(億港元)", names="分類", hole=0.5)
    fig.update_traces(text=filtered_df["分類"], textposition="outside")
    fig.update_layout(xaxis_title="物業類型", showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# Define the base directory
base_dir = os.path.dirname(os.path.abspath(__file__))

# Create columns for displaying images of 10 types of properties
property_images = {
    "住宅": os.path.join(base_dir, 'classphoto/住宅.jpg'),
    "工業": os.path.join(base_dir, 'classphoto/工業.jpg'),
    "商業": os.path.join(base_dir, 'classphoto/商業.jpg'),
    "商場或商鋪或基座商鋪": os.path.join(base_dir, 'classphoto/商場.jpg'),
    "1960年及之前入伙舊樓": os.path.join(base_dir, 'classphoto/舊樓.jpg'),
    "酒店": os.path.join(base_dir, 'classphoto/酒店.jpg'),
    "車位或停車場大廈": os.path.join(base_dir, 'classphoto/車位.jpg'),
    "地盤（包括強拍）": os.path.join(base_dir, 'classphoto/地盤.jpg'),
    "商住": os.path.join(base_dir, 'classphoto/商住.jpg'),
    "其他（包括學校、戲院、農地等）": os.path.join(base_dir, 'classphoto/其他.jpg')
}

columns = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]
property_types = list(property_images.keys())

for col, prop_type in zip(columns, property_types):
    with col:
        image = Image.open(property_images[prop_type])
        if prop_type == "其他（包括學校、戲院、農地等）":
            prop_type = "其他（包括學校、戲院 等）"
        st.image(image, caption=prop_type)
        if type_df_indexed["分類"].isin([prop_type]).any():
            st.metric(label=f"{prop_type}成交宗數", value=type_df_indexed.loc[prop_type, "成交宗數"])
        else:
            st.metric(label=f"{prop_type}成交宗數", value=0)

# View Data
with st.expander("已篩選資料 - 可下載CSV檔案"):
    st.dataframe(filtered_df.style.background_gradient(cmap="Oranges"), 
                 column_order=("資料日期", "地區_18區", "物業地址", "全幢or非全幢", "地盤面積", "成交價(億港元)", "現樓面面積", "現樓面呎價", "可建樓面面積", "重建呎價", "分類", "入伙日期", "照片", "房間數目及每間售價", "賣家", "買家", "資料來源", "新聞連結", "備註"),
                 column_config={
                     "資料日期": st.column_config.DateColumn(
                         "資料日期",
                         format="YYYY.MM.DD",
                     ),
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
    csv = filtered_df.to_csv(index=False, encoding='utf-8')
    st.download_button("Download Data", data=csv, file_name="篩選資料_成交記錄.csv", mime="text/csv", help='Click here to download the data as a CSV file')

# Create Time Series Analysis
filtered_df["month_year"] = filtered_df["Date"].dt.to_period("M")
st.subheader('時間序列分析')

# Convert '成交價(億港元)' to float
filtered_df['成交價(億港元)'] = filtered_df['成交價(億港元)'].astype(float)

# Group by 'month_year' and sum '成交價(億港元)'
linechart = pd.DataFrame(filtered_df.groupby(filtered_df["month_year"].dt.strftime("%Y : %b"))["成交價(億港元)"].sum()).reset_index()
fig2 = px.line(linechart, x="month_year", y="成交價(億港元)", labels={"month_year": "月份"}, height=500, width=1000, template="gridon")
st.plotly_chart(fig2, use_container_width=True)

with st.expander("時間序列統計 - 可下載CSV檔案"):
    st.write(linechart.T.style.background_gradient(cmap="Blues"))
    csv = linechart.to_csv(index=False).encode("utf-8")
    st.download_button('Download Data', data=csv, file_name="TimeSeries.csv", mime='text/csv')


end_time = time.time()

st.write(f"Time taken to run wbdashboard.py: {end_time - start_time} seconds")
