import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ✅ 페이지 기본 설정
st.set_page_config(page_title="혼잡한 곳은 SEA러!", layout="wide")

# ✅ 배경 스타일
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
        font-family: 'Helvetica', sans-serif;
        padding: 0 5vw;
    }
    .title {
        text-align: center;
        font-size: 36px;
        font-weight: 700;
        color: #003366;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #004080;
        margin-bottom: 1.5em;
    }
    .result-card {
        background-color: #ffffffdd;
        padding: 20px;
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 타이틀
st.markdown('<div class="title">혼잡한 곳은 SEA러!</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">전국 해수욕장의 혼잡도를 날짜별로 한눈에 확인해보세요</div>', unsafe_allow_html=True)

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv", encoding="utf-8")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# ✅ 날짜 선택
selected_date = st.date_input("📅 날짜를 선택하세요", value=df["해수욕장일일일자"].min(),
                             min_value=df["해수욕장일일일자"].min(),
                             max_value=df["해수욕장일일일자"].max())

# ✅ 선택한 날짜의 해수욕장 데이터 필터링
filtered = df[df["해수욕장일일일자"] == pd.to_datetime(selected_date)]

# ✅ 지도 생성
m = folium.Map(location=[36.5, 127.8], zoom_start=7)

# ✅ 마커 추가
colors = {"여유": "green", "보통": "orange", "혼잡": "red"}
for _, row in filtered.iterrows():
    tooltip = f"{row['해수욕장이름']} ({row['예상 혼잡도']})"
    popup = f"""
    <b>{row['해수욕장이름']}</b><br>
    📍 {row['시/도']} {row['시/군/구']}<br>
    👥 예상 방문자수: {row['예상 방문자수']}명<br>
    🚦 예상 혼잡도: <b>{row['예상 혼잡도']}</b>
    """
    folium.Marker(
        location=[row["위도"], row["경도"]],
        tooltip=tooltip,
        popup=popup,
        icon=folium.Icon(color=colors.get(row["예상 혼잡도"], "gray"))
    ).add_to(m)

# ✅ 지도 표시
st_folium(m, width=1000, height=600)
