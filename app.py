import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ✅ 페이지 설정 (이건 반드시 제일 위에 있어야 함)
st.set_page_config(
    page_title="혼잡한 곳은 SEA러!",
    layout="wide",
)

# ✅ 배경 그라데이션 스타일
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
        font-family: 'Helvetica', sans-serif;
        padding: 0 5vw;
    }
    .title {
        text-align: center;
        font-size: 38px;
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

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"], format="%Y-%m-%d")
    return df

data = load_data()

# ✅ 헤더
st.markdown("<h1 class='title'>🏖️ 혼잡한 곳은 SEA러!</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</p>", unsafe_allow_html=True)

# ✅ 해수욕장 선택
beaches = sorted(data["해수욕장이름"].unique())
selected_beach = st.selectbox("📍 해수욕장을 선택하세요", beaches)

# ✅ 선택된 해수욕장의 운영 기간 확인
beach_data = data[data["해수욕장이름"] == selected_beach]
min_date = beach_data["해수욕장일일일자"].min()
max_date = beach_data["해수욕장일일일자"].max()

st.markdown(f"📅 <b>{selected_beach}</b>의 예상 운영 기간은 <b>{min_date.date()}</b>부터 <b>{max_date.date()}</b>까지입니다.", unsafe_allow_html=True)

# ✅ 날짜 선택
selected_date = st.date_input("🗓️ 방문 날짜를 선택하세요", min_value=min_date, max_value=max_date)

# ✅ 버튼
if st.button("🔍 예측 결과 보기"):
    filtered = data[(data["해수욕장이름"] == selected_beach) & (data["해수욕장일일일자"] == pd.to_datetime(selected_date))]

    if not filtered.empty:
        visitors = int(filtered["예상 방문자수"].values[0])
        congestion = filtered["예상 혼잡도"].values[0]

        st.markdown(f"""
        <div class="result-card">
            <h4>📅 {selected_date} <b>{selected_beach}</b>의 예측 결과</h4>
            <p>👥 예상 방문자수: <b>{visitors:,}명</b></p>
            <p>📌 예상 혼잡도: <b>{congestion}</b></p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("해당 날짜에 대한 예측 데이터가 없습니다.")

    # ✅ 전국 혼잡도 지도 시각화
    st.markdown("### 🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도")

    selected_day_data = data[data["해수욕장일일일자"] == pd.to_datetime(selected_date)]

    if not selected_day_data.empty:
        # 중심 좌표 설정
        map_center = [selected_day_data["위도"].mean(), selected_day_data["경도"].mean()]
        m = folium.Map(location=map_center, zoom_start=7)

        for _, row in selected_day_data.iterrows():
            color = "green" if row["예상 혼잡도"] == "여유" else "orange" if row["예상 혼잡도"] == "보통" else "red"
            popup_text = f"{row['해수욕장이름']}<br>예상 방문자수: {row['예상 방문자수']:,}명<br>혼잡도: {row['예상 혼잡도']}"
            folium.CircleMarker(
                location=[row["위도"], row["경도"]],
                radius=6,
                color=color,
                fill=True,
                fill_opacity=0.8,
                popup=popup_text
            ).add_to(m)

        st_folium(m, width=1000, height=600)
    else:
        st.warning("선택한 날짜에 대한 전국 혼잡도 데이터가 없습니다.")
