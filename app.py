import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ✅ 페이지 기본 설정
st.set_page_config(page_title="혼잡한 곳은 SEA러!", layout="wide")

# ✅ 배경 그라데이션 스타일 (B안)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #d2edf4);
        font-family: 'Helvetica Neue', sans-serif;
        color: #003366;
        padding: 1rem 5vw;
    }

    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #001f4d;
        margin-bottom: 0.5em;
    }

    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #004080;
        margin-bottom: 2em;
    }

    .section-header {
        font-size: 24px;
        font-weight: 700;
        margin-top: 2rem;
        margin-bottom: 1rem;
        color: #00264d;
    }

    .result-card {
        background-color: #ffffffdd;
        padding: 20px;
        border-radius: 12px;
        margin-top: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        max-width: 650px;
        margin-left: auto;
        margin-right: auto;
    }

    .icon {
        margin-right: 5px;
    }

    </style>
""", unsafe_allow_html=True)

# ✅ 상단 제목
st.markdown('<h1 class="title">🌊 혼잡한 곳은 <span style="color:#0033cc;">SEA</span>러!</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>', unsafe_allow_html=True)

# ✅ CSV 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv", encoding="utf-8")
    df["방문일자"] = pd.to_datetime(df["방문일자"])
    return df

data = load_data()

# ✅ 사용자 입력
beaches = sorted(data["해수욕장"].unique())
selected_beach = st.selectbox("📍 해수욕장을 선택하세요", beaches)

# 선택한 해수욕장의 운영 날짜 범위 표시
beach_data = data[data["해수욕장"] == selected_beach]
min_date = beach_data["방문일자"].min().date()
max_date = beach_data["방문일자"].max().date()
st.markdown(f"🗓️ <b>{selected_beach}</b>의 예상 운영 기간은 <b>{min_date}</b>부터 <b>{max_date}</b>까지입니다.", unsafe_allow_html=True)

selected_date = st.date_input("🧭 방문 날짜를 선택하세요", min_value=min_date, max_value=max_date)

# ✅ 예측 결과 표시
filtered = data[(data["해수욕장"] == selected_beach) & (data["방문일자"] == pd.to_datetime(selected_date))]

if not filtered.empty:
    visitors = int(filtered["예상방문자수"].values[0])
    congestion = filtered["혼잡도"].values[0]

    st.markdown(f"""
        <div class="result-card">
            <h4>📅 {selected_date} {selected_beach}의 예측 결과</h4>
            <p>👥 <b>예상 방문자수:</b> {visitors:,}명</p>
            <p>📍 <b>예상 혼잡도:</b> <span style="color: {'green' if congestion=='여유' else 'orange' if congestion=='보통' else 'red'};"><b>{congestion}</b></span></p>
        </div>
    """, unsafe_allow_html=True)
else:
    st.warning("선택한 해수욕장과 날짜에 대한 예측 데이터가 없습니다.")

# ✅ 전체 지도 시각화
st.markdown('<h3 class="section-header">🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도</h3>', unsafe_allow_html=True)

selected_day_data = data[data["방문일자"] == pd.to_datetime(selected_date)]

if selected_day_data.empty:
    st.warning("선택한 날짜에 대한 전국 해수욕장 데이터가 없습니다.")
else:
    # 지도 중심
    map_center = [selected_day_data["위도"].mean(), selected_day_data["경도"].mean()]
    m = folium.Map(location=map_center, zoom_start=7)

    def get_color(level):
        if level == "여유":
            return "green"
        elif level == "보통":
            return "orange"
        else:
            return "red"

    for _, row in selected_day_data.iterrows():
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=6,
            color=get_color(row["혼잡도"]),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['해수욕장']}<br>방문자수: {row['예상방문자수']}명<br>혼잡도: {row['혼잡도']}"
        ).add_to(m)

    st_folium(m, width=900, height=500)
