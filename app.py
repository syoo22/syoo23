# 이전 코드에서 HTML 태그들이 문자열 안에서 들여쓰기로 인해 오류가 발생함.
# HTML 스타일 블록을 """로 감쌈과 동시에 줄 맨 앞에 들여쓰기를 제거하여 오류 수정.

# 전체 수정된 app.py 코드 다시 생성
app_py_code_fixed = """
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# ✅ 페이지 설정
st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="centered")

# ✅ 데이터 로드 함수
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# ✅ 스타일 적용
st.markdown(\"""
<style>
.stApp {
    background: linear-gradient(to bottom, #b3e0f7, #dff6fd);
    font-family: 'Segoe UI', sans-serif;
}
.title {
    font-size: 2.6rem;
    font-weight: 800;
    color: #003366;
    text-align: center;
}
.subtitle {
    text-align: center;
    font-size: 1.1rem;
    color: #003366;
    margin-bottom: 2rem;
}
</style>
\""", unsafe_allow_html=True)

# ✅ 제목
st.markdown('<div class="title">🌊 혼잡한 바다는 <span style="color:#0049b7">SEA</span>러!</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>', unsafe_allow_html=True)

# ✅ 시/도, 시/군/구, 해수욕장 선택
sido = st.selectbox("📌 시/도를 선택하세요", sorted(df["시/도"].unique()))
sigungu_list = df[df["시/도"] == sido]["시/군/구"].unique()
sigungu = st.selectbox("🗺️ 시/군/구를 선택하세요", sorted(sigungu_list))
beach_list = df[(df["시/도"] == sido) & (df["시/군/구"] == sigungu)]["해수욕장이름"].unique()
selected_beach = st.selectbox("📍 해수욕장을 선택하세요", sorted(beach_list))

# ✅ 날짜 선택
date_list = df["해수욕장일일일자"].dt.date.unique()
selected_date = st.selectbox("📅 방문 날짜를 선택하세요", sorted(date_list))

# ✅ 예측 결과 필터링
filtered = df[
    (df["시/도"] == sido) &
    (df["시/군/구"] == sigungu) &
    (df["해수욕장이름"] == selected_beach) &
    (df["해수욕장일일일자"].dt.date == selected_date)
]

if not filtered.empty:
    visitors = int(filtered["예상 방문자수"].values[0])
    congestion = filtered["예상 혼잡도"].values[0]

    st.markdown("### 🗓️ {} {}의 예측 결과".format(selected_date, selected_beach))
    st.markdown("- 👥 예상 방문자수: **{}명**".format(visitors))
    st.markdown("- 📌 예상 혼잡도: **{}**".format(congestion))

# ✅ 선택한 날짜 전체 해수욕장 혼잡도 지도
st.markdown("### 🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도")

selected_day_data = df[df["해수욕장일일일자"].dt.date == selected_date]
if not selected_day_data.empty:
    def get_color(level):
        if level == "혼잡":
            return "red"
        elif level == "보통":
            return "orange"
        else:
            return "green"

    map_center = [selected_day_data["위도"].mean(), selected_day_data["경도"].mean()]
    m = folium.Map(location=map_center, zoom_start=7)

    for _, row in selected_day_data.iterrows():
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=6,
            color=get_color(row["예상 혼잡도"]),
            fill=True,
            fill_opacity=0.7,
            popup=f"{row['해수욕장이름']}<br>예상 방문자수: {row['예상 방문자수']}명<br>혼잡도: {row['예상 혼잡도']}"
        ).add_to(m)

    st_folium(m, width=700, height=500)
else:
    st.warning("해당 날짜에 대한 해수욕장 데이터가 없습니다.")
"""

# 저장
with open("/mnt/data/app.py", "w", encoding="utf-8") as f:
    f.write(app_py_code_fixed)

"✅ 오류 수정된 app.py 파일 저장 완료!"
