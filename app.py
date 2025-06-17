import streamlit as st
import pandas as pd
from datetime import date
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="wide")

# 👉 스타일 적용
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
        font-family: 'Helvetica', sans-serif;
        padding: 0 5vw;
    }
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: 800;
        color: #001F3F;
        margin-bottom: 0.2em;
    }
    .title .blue {
        color: #0074D9;
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
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🌊 혼잡한 바다는 <span class='blue'>SEA</span>러!</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)

# ✅ 데이터 로딩
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# ✅ 선택 항목 구성
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

# ✅ 시/도 선택
selected_sido = st.selectbox("📍 시/도를 선택하세요", sido_list)

if selected_sido:
    selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_dict[selected_sido])

    if selected_sigungu:
        selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_dict[(selected_sido, selected_sigungu)])
        beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
        open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
        st.markdown(f"📅 **{selected_beach}**의 예상 운영 기간은 **{open_date}부터 {close_date}까지**입니다.")

        selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)

        if st.button("🔍 예측 결과 보기"):
            row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
            if not row.empty:
                visitors = int(row["예상 방문자수"].values[0])
                level = row["예상 혼잡도"].values[0]
                st.markdown(f"<div class='result-card'><h4>📅 {selected_date} {selected_beach}의 예측 결과</h4><br>👥 예상 방문자수: <b>{visitors:,}명</b><br>🔵 예상 혼잡도: <b>{level}</b></div>", unsafe_allow_html=True)

                # ✅ 같은 시/도 내 덜 혼잡한 해수욕장 추천
                st.markdown("### 🧭 같은 시/도 내 덜 혼잡한 해수욕장 추천")
                alt = df[
                    (df["시/도"] == row["시/도"].values[0]) &
                    (df["해수욕장일일일자"] == pd.to_datetime(selected_date)) &
                    (df["예상 혼잡도"].isin(["여유", "보통"])) &
                    (df["해수욕장이름"] != selected_beach)
                ][["시/군/구", "해수욕장이름", "예상 방문자수", "예상 혼잡도"]].sort_values("예상 방문자수")

                if alt.empty:
                    st.info("같은 시/도 내에 덜 혼잡한 다른 해수욕장이 없어요 😥")
                else:
                    st.dataframe(alt.rename(columns={
                        "시/군/구": "시/군/구",
                        "해수욕장이름": "해수욕장",
                        "예상 방문자수": "예상 방문자수(명)",
                        "예상 혼잡도": "혼잡도"
                    }), hide_index=True)
            else:
                st.warning("해당 날짜에 대한 예측 데이터가 없습니다.")
