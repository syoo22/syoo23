
import streamlit as st
import pandas as pd
from datetime import datetime

# ✅ 페이지 설정
st.set_page_config(page_title="해수욕장 방문자 예측 시스템", layout="wide")

# ✅ 바다색 배경 스타일
st.markdown(
    """
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
    """,
    unsafe_allow_html=True
)

# ✅ 제목
st.markdown("<div class='title'>🏖️ 2025 해수욕장 방문자 예측 시스템</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>", unsafe_allow_html=True)

# ✅ 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# ✅ 해수욕장 선택
st.markdown("📍 해수욕장을 선택하세요")
beach_list = df["해수욕장이름"].unique()
selected_beach = st.selectbox("", beach_list)

# ✅ 운영 기간 정보
sample_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
start_date = sample_dates.min().date()
end_date = sample_dates.max().date()
st.markdown(
    f"📅 <b>{selected_beach}</b>의 예상 운영 기간은 <b>{start_date}부터 {end_date}까지</b>입니다.",
    unsafe_allow_html=True
)

# ✅ 날짜 선택
st.markdown("🗓️ 방문 날짜를 선택하세요")
selected_date = st.date_input("", value=start_date, min_value=start_date, max_value=end_date)

# ✅ 예측 결과 확인
if st.button("🔍 예측 결과 보기"):
    filtered = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"].dt.date == selected_date)]

    if not filtered.empty:
        visitors = int(filtered["예상 방문자수"].values[0])
        congestion = filtered["혼잡도"].values[0]
        color = "red" if congestion == "혼잡" else "orange" if congestion == "보통" else "green"

        st.markdown(
            f"""
            <div class="result-card">
                <h4>📅 {selected_date} <strong>{selected_beach}</strong>의 예측 결과</h4>
                <p>👥 예상 방문자수: <strong>{visitors:,}명</strong></p>
                <p>📌 예상 혼잡도: <strong style="color:{color}">{congestion}</strong></p>
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.warning("해당 날짜에 대한 예측 정보가 없습니다.")
