
import streamlit as st
st.set_page_config(page_title="해수욕장 방문자 예측 시스템", layout="wide")

import pandas as pd
import folium
from streamlit_folium import st_folium
from datetime import date

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# ✅ 시/도 → 시/군/구 → 해수욕장 필터링용 딕셔너리 생성
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

# ✅ 스타일
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

# ✅ 제목
st.markdown("<div class='title'>🏖️ 2025 해수욕장 방문자 예측 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:17px; margin-bottom:1rem;'>📍 전국 해수욕장의 예상 방문자 수와 혼잡도를 날짜별로 확인해보세요.</p>", unsafe_allow_html=True)

# ✅ 사용자 선택 UI
selected_sido = st.selectbox("📍 시/도를 선택하세요", sido_list)

if selected_sido:
    selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_dict[selected_sido])

    if selected_sigungu:
        selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_dict[(selected_sido, selected_sigungu)])

        # 운영기간 안내
        beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
        open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
        st.markdown(f"📅 **{selected_beach}**의 예상 운영 기간은 **{open_date}부터 {close_date}까지**입니다.")

        # 날짜 선택
        selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)

        if st.button("🔍 예측 결과 보기"):
            row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]

            if not row.empty:
                visitors = int(row["예상 방문자수"].values[0])
                level = row["예상 혼잡도"].values[0]
                st.markdown(f"<div class='result-card'><h4>📅 {selected_date} {selected_beach}의 예측 결과</h4><br>👥 예상 방문자수: <b>{visitors:,}명</b><br>🔵 예상 혼잡도: <b>{level}</b></div>", unsafe_allow_html=True)
            else:
                st.warning("해당 날짜에 대한 예측 데이터가 없습니다.")
