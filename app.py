
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ✅ 페이지 설정
st.set_page_config(page_title="2025 해수욕장 방문자 예측 시스템", layout="wide")

# ✅ 배경 스타일 (바다색 그라데이션)
st.markdown(
    """
    <style>
    body {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
    }
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: 700;
        color: #003366;
        margin-bottom: 0.5em;
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
        border-radius: 10px;
        margin-top: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        max-width: 700px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ✅ 데이터 로드
@st.cache_data
def load_data():
    return pd.read_csv("2025_해수욕장_예측결과_최종.csv")

data = load_data()

# ✅ 제목 및 안내
st.markdown("<div class='title'>🏖️ 2025 해수욕장 방문자 예측 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)

# ✅ 해수욕장 선택
selected_beach = st.selectbox("📍 해수욕장을 선택하세요", sorted(data["해수욕장"].unique()))

# ✅ 선택한 해수욕장의 운영 기간
beach_df = data[data["해수욕장"] == selected_beach]
start_date = beach_df["날짜"].min()
end_date = beach_df["날짜"].max()
st.markdown(f"🗓️ <b>{selected_beach}</b>의 예상 운영 기간은 <b>{start_date}</b>부터 <b>{end_date}</b>까지입니다.", unsafe_allow_html=True)

# ✅ 날짜 선택
selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=datetime.strptime(start_date, "%Y-%m-%d"))

# ✅ 예측 결과 버튼
if st.button("🔍 예측 결과 보기"):
    selected_date_str = selected_date.strftime("%Y-%m-%d")
    filtered = data[(data["해수욕장"] == selected_beach) & (data["날짜"] == selected_date_str)]

    if not filtered.empty:
        visitors = int(filtered["예상방문자수"].values[0])
        congestion = filtered["혼잡도"].values[0]

        result_html = f"""
        <div class='result-card'>
            <h4>📅 {selected_date_str} <b>{selected_beach}</b>의 예측 결과</h4>
            <p>👥 예상 방문자수: <b>{visitors:,}명</b></p>
            <p>📌 예상 혼잡도: <b>{congestion}</b></p>
        </div>
        """
        st.markdown(result_html, unsafe_allow_html=True)
    else:
        st.warning("해당 날짜의 예측 정보가 없습니다.")

# ✅ 지도 섹션
st.markdown("<h3>🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도</h3>", unsafe_allow_html=True)

selected_day_data = data[data["날짜"] == selected_date.strftime("%Y-%m-%d")]

if not selected_day_data.empty:
    m = folium.Map(
        location=[selected_day_data["위도"].mean(), selected_day_data["경도"].mean()],
        zoom_start=7
    )

    # 색상 매핑
    color_dict = {"여유": "green", "보통": "orange", "혼잡": "red"}

    for _, row in selected_day_data.iterrows():
        folium.CircleMarker(
            location=(row["위도"], row["경도"]),
            radius=7,
            popup=f"{row['해수욕장']} ({row['혼잡도']})",
            color=color_dict.get(row["혼잡도"], "gray"),
            fill=True,
            fill_color=color_dict.get(row["혼잡도"], "gray"),
            fill_opacity=0.7
        ).add_to(m)

    st_folium(m, width=900, height=550)
else:
    st.info("선택한 날짜의 전국 해수욕장 예측 데이터가 없습니다.")
