import streamlit as st
import pandas as pd
from datetime import date
import folium
from streamlit_folium import st_folium

# 1️⃣ 기본 설정 ─────────────────────────────────────────────────
st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="wide")

# 2️⃣ CSS (바다색 그라데이션) ────────────────────────────────────
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to bottom, #a6d9f7, #e4f8ff);
    font-family: 'Segoe UI', sans-serif;
    padding: 0 5vw;
}
.title {
    text-align:center; font-size:40px; font-weight:800; color:#003366;
}
.title .blue { color:#0066ff; }
.subtitle {
    text-align:center; font-size:17px; color:#004080; margin-bottom:2rem;
}
.result-card{
    background:#ffffffdd; padding:20px; border-radius:10px;
    box-shadow:0 4px 8px rgba(0,0,0,0.1); max-width:600px; margin:20px auto;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌊 혼잡한 바다는 <span class="blue">SEA</span>러!</div>',
            unsafe_allow_html=True)
st.markdown('<div class="subtitle">해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>',
            unsafe_allow_html=True)

# 3️⃣ 데이터 로드 ────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# 4️⃣ 선택 리스트 준비 ───────────────────────────────────────────
sido_list = sorted(df["시/도"].dropna().unique())

# 시/군/구 딕셔너리
sigungu_dict = {
    sido: sorted(df[df["시/도"] == sido]["시/군/구"].dropna().unique())
    for sido in sido_list
}

# (시/도, 시/군/구) → 해수욕장 리스트 딕셔너리
beach_dict = {}
for sido in sido_list:
    for sigungu in sigungu_dict[sido]:
        beaches = df[(df["시/도"] == sido) & (df["시/군/구"] == sigungu)]["해수욕장이름"].dropna().unique()
        beach_dict[(sido, sigungu)] = sorted(beaches)

# 5️⃣ 위젯: 시/도 → 시/군/구 → 해수욕장 → 날짜 ──────────────────
selected_sido = st.selectbox("📌 시/도를 선택하세요", sido_list)

# 시/군/구
sigungu_options = sigungu_dict.get(selected_sido, [])
selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_options)

# 해수욕장
beach_options = beach_dict.get((selected_sido, selected_sigungu), [])
if beach_options:
    selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_options)
else:
    selected_beach = None
    st.warning("선택한 시/군/구에 등록된 해수욕장이 없습니다.")

# 날짜
if selected_beach:
    beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
    open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
    st.markdown(f"📅 **{selected_beach}** 운영 기간: **{open_date} ~ {close_date}**")

    selected_date = st.date_input("📅 방문 날짜를 선택하세요",
                                  value=open_date,
                                  min_value=open_date,
                                  max_value=close_date)
else:
    selected_date = None

# 6️⃣ 예측 결과 & 추천 ────────────────────────────────────────────
if st.button("🔍 예측 결과 보기") and selected_beach and selected_date:
    row = df[(df["해수욕장이름"] == selected_beach) &
             (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
    
    if not row.empty:
        visitors = int(row["예상 방문자수"].iloc[0])
        level = row["예상 혼잡도"].iloc[0]

        st.markdown(f"""
        <div class="result-card">
            <h4>📅 {selected_date} {selected_beach} 예측 결과</h4>
            👥 예상 방문자수: <b>{visitors:,}명</b><br>
            🚦 예상 혼잡도: <b>{level}</b>
        </div>
        """, unsafe_allow_html=True)

        # 덜 혼잡한 추천
        st.markdown("### 🧭 같은 시/도 내 덜 혼잡한 해수욕장 추천")
        alt = df[
            (df["시/도"] == selected_sido) &
            (df["해수욕장일일일자"] == pd.to_datetime(selected_date)) &
            (df["예상 혼잡도"].isin(["여유", "보통"])) &
            (df["해수욕장이름"] != selected_beach)
        ][["시/군/구", "해수욕장이름", "예상 방문자수", "예상 혼잡도"]].sort_values("예상 방문자수")
        
        if alt.empty:
            st.info("같은 시/도 내 덜 혼잡한 다른 해수욕장이 없어요 😥")
        else:
            st.dataframe(
                alt.rename(columns={
                    "시/군/구": "시/군/구",
                    "해수욕장이름": "해수욕장",
                    "예상 방문자수": "예상 방문자수(명)",
                    "예상 혼잡도": "혼잡도"
                }),
                hide_index=True
            )
    else:
        st.warning("해당 날짜에 대한 예측 데이터가 없습니다.")
