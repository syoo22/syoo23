
import streamlit as st
st.set_page_config(page_title="해수욕장 방문자 예측 시스템", layout="wide")

import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date

@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

st.title("🗺️ 전국 해수욕장 혼잡도 지도")

# ✅ 사용자 날짜 선택
selected_date = st.date_input("📅 지도에 표시할 날짜를 선택하세요", value=date(2025, 8, 1))

# ✅ 해당 날짜에 해당하는 해수욕장만 필터링
filtered = df[df["해수욕장일일일자"] == pd.to_datetime(selected_date)].dropna(subset=["위도", "경도"])

if filtered.empty:
    st.warning("해당 날짜에 대한 해수욕장 정보가 없습니다.")
else:
    # ✅ 지도 중심을 평균 좌표로 설정
    map_center = [filtered["위도"].mean(), filtered["경도"].mean()]
    m = folium.Map(location=map_center, zoom_start=7)

    for _, row in filtered.iterrows():
        level = row["예상 혼잡도"]
        color = "green" if level == "여유" else "orange" if level == "보통" else "red"
        folium.CircleMarker(
            location=[row["위도"], row["경도"]],
            radius=6,
            color=color,
            fill=True,
            fill_opacity=0.8,
            fill_color=color,
            popup=folium.Popup(
                f"<b>{row['해수욕장이름']}</b><br>예상 방문자수: {int(row['예상 방문자수'])}명<br>혼잡도: {level}",
                max_width=250
            )
        ).add_to(m)

    # ✅ 지도 출력
    st.markdown("#### 🗺️ 혼잡도 색상: 🟢 여유 | 🟡 보통 | 🔴 혼잡", unsafe_allow_html=True)
    st_data = st_folium(m, width=1000, height=600)
