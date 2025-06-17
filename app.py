
import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import datetime

st.set_page_config(page_title="2025 해수욕장 방문자 예측 시스템", layout="wide")

with open("custom_style.css") as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

st.markdown("<div class='title'>🏖️ 2025 해수욕장 방문자 예측 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)
st.markdown("📍 전국 해수욕장의 예상 방문자 수와 혼잡도를 날짜별로 확인해보세요.")

sido = st.selectbox("📍 시/도를 선택하세요", sorted(df["시/도"].unique()))
sigungu_options = sorted(df[df["시/도"] == sido]["시/군/구"].unique())
sigungu = st.selectbox("🌅 시/군/구를 선택하세요", sigungu_options)
beach_options = sorted(df[(df["시/도"] == sido) & (df["시/군/구"] == sigungu)]["해수욕장이름"].unique())
selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_options)

date_options = sorted(df["해수욕장일일일자"].dt.date.unique())
selected_date = st.selectbox("📅 방문 날짜를 선택하세요", date_options, index=0)

if "show_result" not in st.session_state:
    st.session_state["show_result"] = False

if st.button("🔍 예측 결과 보기"):
    st.session_state["show_result"] = True

if st.session_state["show_result"]:
    filtered = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"].dt.date == selected_date)]

    if not filtered.empty:
        visitors = int(filtered["예측방문자수"].values[0])
        level = filtered["혼잡도"].values[0]
        st.markdown(f'''
<div class="result-card">
    <h4>📅 {selected_date} <strong>{selected_beach}</strong>의 예측 결과</h4>
    <p>👥 <strong>예상 방문자수:</strong> {visitors:,}명</p>
    <p>📌 <strong>예상 혼잡도:</strong> <span style="color: {'green' if level=='여유' else 'orange' if level=='보통' else 'red'}">{level}</span></p>
</div>
        ''', unsafe_allow_html=True)

        st.markdown("### 🧭 같은 시/도 내 덜 혼잡한 해수욕장 추천")
        same_region = df[(df["시/도"] == sido) & (df["해수욕장일일일자"].dt.date == selected_date)]
        alternatives = same_region[same_region["혼잡도"] == "여유"]
        if not alternatives.empty:
            st.dataframe(alternatives[["시/군/구", "해수욕장이름", "예측방문자수", "혼잡도"]].sort_values("예측방문자수"), hide_index=True)
        else:
            st.info("같은 시/도 내 여유 해수욕장이 없습니다.")

st.markdown("### 🌍 선택한 날짜 기준 전국 해수욕장 혼잡도 지도")

map_data = df[df["해수욕장일일일자"].dt.date == selected_date].dropna(subset=["위도", "경도"])
map_center = [map_data["위도"].mean(), map_data["경도"].mean()]
m = folium.Map(location=map_center, zoom_start=7)

for _, row in map_data.iterrows():
    color = {"여유": "green", "보통": "orange", "혼잡": "red"}[row["혼잡도"]]
    folium.CircleMarker(
        location=[row["위도"], row["경도"]],
        radius=6,
        color=color,
        fill=True,
        fill_opacity=0.8,
        popup=f"{row['해수욕장이름']}<br>예상 방문자: {int(row['예측방문자수'])}명<br>혼잡도: {row['혼잡도']}",
    ).add_to(m)

legend_html = '''
<div style="position: fixed; bottom: 40px; left: 40px; background-color: white; padding: 10px; border-radius: 5px; box-shadow: 2px 2px 5px gray; font-size:14px;">
<b style="color:green">여유</b> &nbsp;&nbsp;
<b style="color:orange">보통</b> &nbsp;&nbsp;
<b style="color:red">혼잡</b>
</div>
'''
m.get_root().html.add_child(folium.Element(legend_html))
st_folium(m, width=1000, height=500)
