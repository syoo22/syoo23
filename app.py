import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ✅ 페이지 설정
st.set_page_config(page_title="혼잡한 곳은 SEA러!", layout="wide")

# ✅ 배경 스타일 (A안: CSS 없이 배경 포함)
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
        font-family: 'Helvetica', sans-serif;
        padding: 0 5vw;
    }
    .title {
        text-align: center;
        font-size: 42px;
        font-weight: 800;
        color: #003366;
        margin-bottom: 0.2em;
    }
    .subtitle {
        text-align: center;
        font-size: 18px;
        color: #004080;
        margin-bottom: 2em;
    }
    .result-card {
        background-color: #ffffffdd;
        padding: 20px;
        border-radius: 15px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

# ✅ 제목
st.markdown("<div class='title'>🌊 혼잡한 곳은 <b>SEA러!</b></div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)

# ✅ 데이터 불러오기
data = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
data["방문일자"] = pd.to_datetime(data["방문일자"])

# ✅ 해수욕장 선택
st.markdown("📍 해수욕장을 선택하세요")
selected_beach = st.selectbox(" ", sorted(data["해수욕장"].unique()))

# ✅ 운영 기간 안내
beach_data = data[data["해수욕장"] == selected_beach]
min_date = beach_data["방문일자"].min().strftime("%Y-%m-%d")
max_date = beach_data["방문일자"].max().strftime("%Y-%m-%d")
st.markdown(f"🗓️ <b>{selected_beach}</b>의 예상 운영 기간은 <b>{min_date}</b>부터 <b>{max_date}</b>까지입니다.", unsafe_allow_html=True)

# ✅ 날짜 선택
selected_date = st.date_input("🗓 방문 날짜를 선택하세요", value=beach_data["방문일자"].min(), min_value=beach_data["방문일자"].min(), max_value=beach_data["방문일자"].max())

# ✅ 버튼 클릭 시 결과 출력
if st.button("🔍 예측 결과 보기"):
    filtered = data[(data["해수욕장"] == selected_beach) & (data["방문일자"] == pd.to_datetime(selected_date))]

    if not filtered.empty:
        visitors = int(filtered["예상방문자수"].values[0])
        congestion = filtered["혼잡도"].values[0]

        st.markdown(f"""
        <div class='result-card'>
            <h4>📅 {selected_date} {selected_beach}의 예측 결과</h4>
            <p>👥 예상 방문자수: <b>{visitors}명</b></p>
            <p>📌 예상 혼잡도: <b>{congestion}</b></p>
        </div>
        """, unsafe_allow_html=True)

    # ✅ 전체 지도 시각화
    st.markdown("<h3>🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도</h3>", unsafe_allow_html=True)

    selected_day_data = data[data["방문일자"] == pd.to_datetime(selected_date)]

    if not selected_day_data.empty:
        # 지도 중심
        map_center = [selected_day_data["위도"].mean(), selected_day_data["경도"].mean()]
        m = folium.Map(location=map_center, zoom_start=7)

        # 혼잡도 색상 설정 함수
        def get_color(level):
            if level == "여유":
                return "green"
            elif level == "보통":
                return "orange"
            else:
                return "red"

        # 마커 추가
        for _, row in selected_day_data.iterrows():
            folium.CircleMarker(
                location=[row["위도"], row["경도"]],
                radius=6,
                color=get_color(row["혼잡도"]),
                fill=True,
                fill_opacity=0.7,
                popup=f"{row['해수욕장']}<br>방문자수: {row['예상방문자수']}명<br>혼잡도: {row['혼잡도']}"
            ).add_to(m)

        # 지도 표시
        st_folium(m, width=900, height=500)
