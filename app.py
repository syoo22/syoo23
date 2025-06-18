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

sido_list = sorted(df["시/도"].dropna().unique())
sigungu_dict = {
    sido: sorted(df[df["시/도"] == sido]["시/군/구"].dropna().unique())
    for sido in sido_list
}
beach_dict = {
    (sido, sigungu): sorted(df[
        (df["시/도"] == sido) & (df["시/군/구"] == sigungu)
    ]["해수욕장이름"].dropna().unique())
    for sido in sido_list
    for sigungu in sigungu_dict[sido]
}

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

st.markdown("<div class='title'>🏖️ 2025 해수욕장 방문자 예측 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:17px; margin-bottom:1rem;'>📍 전국 해수욕장의 예상 방문자 수와 혼잡도를 날짜별로 확인해보세요.</p>", unsafe_allow_html=True)

selected_sido = st.selectbox("📍 시/도를 선택하세요", sido_list)

if selected_sido:
    selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_dict[selected_sido])

    if selected_sigungu:
        selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_dict[(selected_sido, selected_sigungu)])
        beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
        open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
        st.markdown(f"📅 **{selected_beach}**의 예상 운영 기간은 **{open_date}부터 {close_date}까지**입니다.")

        selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)

# 1. 버튼 상태 세션으로 관리
if "show_result" not in st.session_state:
    st.session_state.show_result = False

if st.button("🔍 예측 결과 보기"):
    st.session_state.show_result = True

# 2. 버튼 클릭 후 계속 유지되도록 조건 변경
if st.session_state.show_result:
    row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
    if not row.empty:
        visitors = int(row["예상 방문자수"].values[0])
        level = row["예상 혼잡도"].values[0]
        st.markdown(f"<div class='result-card'>...</div>", unsafe_allow_html=True)

        st.markdown("### 🧭 같은 시/도 내 덜 혼잡한 해수욕장 추천")
        alt = df[
            (df["시/도"] == row["시/도"].values[0]) &
            (df["해수욕장일일일자"] == pd.to_datetime(selected_date)) &
            (df["예상 혼잡도"].isin(["여유", "보통"])) &
            (df["해수욕장이름"] != selected_beach)
        ][["시/군/구", "해수욕장이름", "예상 방문자수", "예상 혼잡도", "위도", "경도"]].sort_values("예상 방문자수")

        if alt.empty:
            st.info("같은 시/도 내에 덜 혼잡한 다른 해수욕장이 없어요 😥")
        else:
            st.dataframe(...)  # 표 출력

            # 지도 시각화
            st.markdown("### 🗺️ 덜 혼잡한 해수욕장 위치 보기")
            selected_loc = row[["위도", "경도"]].values[0]
            m = folium.Map(location=selected_loc, zoom_start=10)
            congestion_color = {"여유": "green", "보통": "orange"}

            for _, r in alt.iterrows():
                folium.CircleMarker(
                    location=(r["위도"], r["경도"]),
                    radius=8,
                    color=congestion_color.get(r["예상 혼잡도"], "gray"),
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"<b>{r['해수욕장이름']}</b><br>👥 {int(r['예상 방문자수']):,}명<br>혼잡도: {r['예상 혼잡도']}", max_width=200
                    )
                ).add_to(m)

            st_folium(m, width=700, height=500)
    else:
        st.warning("해당 날짜에 대한 예측 데이터가 없습니다.")
