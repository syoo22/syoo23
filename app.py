
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

st.title("🏖️ 2025 해수욕장 방문자 예측 시스템")
st.markdown("해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!")
st.markdown("📍 전국 해수욕장의 예상 방문자 수와 혼잡도를 날짜별로 확인해보세요.")

selected_sido = st.selectbox("📍 시/도를 선택하세요", sido_list)

if selected_sido:
    selected_sigungu = st.selectbox("🌅 시/군/구를 선택하세요", sigungu_dict[selected_sido])

    if selected_sigungu:
        selected_beach = st.selectbox("🏝️ 해수욕장을 선택하세요", beach_dict[(selected_sido, selected_sigungu)])
        beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
        open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
        st.markdown(f"📅 **{selected_beach}**의 예상 운영 기간은 **{open_date}부터 {close_date}까지**입니다.")

        selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)

        show_result = st.button("🔍 예측 결과 보기")

        if show_result:
            row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
            if not row.empty:
                visitors = int(row["예상 방문자수"].values[0])
                level = row["예상 혼잡도"].values[0]
                st.markdown(f"<div style='background-color:#f9f9f9;padding:1rem;border-radius:10px;box-shadow:0 2px 4px rgba(0,0,0,0.1)'><b>📅 {selected_date} {selected_beach}의 예측 결과</b><br>👥 예상 방문자수: <b>{visitors:,}명</b><br>🔵 예상 혼잡도: <b>{level}</b></div>", unsafe_allow_html=True)

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

        # ✅ 지도는 항상 아래 고정 출력 (렌더링 조건과 분리)
        st.markdown("### 🗺️ 선택한 날짜 기준 전국 해수욕장 혼잡도 지도")

        filtered = df[df["해수욕장일일일자"] == pd.to_datetime(selected_date)].dropna(subset=["위도", "경도"])
        filtered["위도"] = pd.to_numeric(filtered["위도"], errors="coerce")
        filtered["경도"] = pd.to_numeric(filtered["경도"], errors="coerce")
        filtered = filtered.dropna(subset=["위도", "경도"])

        if not filtered.empty:
            map_center = [filtered["위도"].mean(), filtered["경도"].mean()]
            m = folium.Map(location=map_center, zoom_start=7)

            for _, row2 in filtered.iterrows():
                color = "green" if row2["예상 혼잡도"] == "여유" else "orange" if row2["예상 혼잡도"] == "보통" else "red"
                folium.CircleMarker(
                    location=[row2["위도"], row2["경도"]],
                    radius=6,
                    color=color,
                    fill=True,
                    fill_color=color,
                    fill_opacity=0.8,
                    popup=f"{row2['해수욕장이름']}<br>방문자수: {int(row2['예상 방문자수'])}명<br>혼잡도: {row2['예상 혼잡도']}"
                ).add_to(m)

            st.markdown("🟢 여유 &nbsp;&nbsp;&nbsp; 🟡 보통 &nbsp;&nbsp;&nbsp; 🔴 혼잡", unsafe_allow_html=True)
            st_folium(m, width=1000, height=600)
        else:
            st.warning("해당 날짜에 대한 지도 데이터가 없습니다.")
