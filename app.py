
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ✅ 페이지 설정
st.set_page_config(page_title="2025 해수욕장 방문자 예측 시스템", layout="wide")

# ✅ 배경 색 설정 (그라데이션)
page_bg = """
<style>
.stApp {
    background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
}
</style>
"""
st.markdown(page_bg, unsafe_allow_html=True)

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("2025_해수욕장_예측결과_최종.csv")

df = load_data()
df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])

# ✅ 해수욕장 목록
beach_list = sorted(df["해수욕장이름"].unique())

# ✅ 사용자 입력
st.title("🏖️ 2025 해수욕장 방문자 예측 시스템")
st.markdown("해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!")

selected_beach = st.selectbox("📍 해수욕장을 선택하세요", beach_list)
selected_date = st.date_input("📅 방문 날짜를 선택하세요", pd.to_datetime("2025-06-01"))

# ✅ 예측 결과 표시
if st.button("🔍 예측 결과 보기"):
    filtered = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]

    if filtered.empty:
        st.warning("선택한 해수욕장의 해당 날짜 예측 데이터가 없습니다.")
    else:
        visitors = int(filtered["예상 방문자수"].values[0])
        congestion = filtered["예상 혼잡도"].values[0]

        st.markdown(f"### 📅 {selected_date.strftime('%Y-%m-%d')} **{selected_beach}**의 예측 결과")
        st.markdown(f"- 👥 예상 방문자수: **{visitors:,}명**")
        st.markdown(f"- 📌 예상 혼잡도: **{congestion}**")

# ✅ 전체 혼잡도 지도 시각화
st.markdown("## 🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도")

selected_day_data = df[df["해수욕장일일일자"] == pd.to_datetime(selected_date)]
map_center = [selected_day_data["위도"].mean(), selected_day_data["경도"].mean()]
m = folium.Map(location=map_center, zoom_start=7)

for _, row in selected_day_data.iterrows():
    color = {"여유": "green", "보통": "orange", "혼잡": "red"}.get(row["예상 혼잡도"], "gray")
    folium.CircleMarker(
        location=(row["위도"], row["경도"]),
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=f"{row['해수욕장이름']} ({row['예상 혼잡도']})"
    ).add_to(m)

st_folium(m, width=1100, height=550)
