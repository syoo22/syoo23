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

# 시/도, 시군구, 해수욕장 딕셔너리
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

# 스타일
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
    /* ✅ 추가: 지도 아래 흰 여백 제거용 */
    .element-container:has(iframe) {
        padding-bottom: 0px !important;
        margin-bottom: 0px !important;
    }

    iframe {
    display: block;
    margin: 0 auto;
    height: 600px !important;
    margin-bottom: -20px !important; /* ✅ 하단 공백 강제 제거 */
    padding-bottom: 0px !important;
    }

    .block-container {
        padding-bottom: 0rem !important;
    }

        /* ✅ 추가: html/body 및 최상위 block 여백 제거 */
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        overflow-x: hidden;
    }

    section.main > div.block-container {
        padding-bottom: 0rem !important;
        margin-bottom: 0rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# 제목
st.markdown("<div class='title'>🏖️ 혼잡한 바다는 SEA러! </div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>이 서비스는 해수욕장 혼잡 문제를 해결하기 위해 제작된 해수욕장 방문자 예측 공공 서비스입니다.</div>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; font-size:17px; margin-bottom:1rem;'>📍 해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!.</p>", unsafe_allow_html=True)

# 선택 영역
selected_sido = st.selectbox("📍 시/도를 선택하세요", sido_list)

if selected_sido:
    selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_dict[selected_sido])

    if selected_sigungu:
        selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_dict[(selected_sido, selected_sigungu)])
        beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
        open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
        st.markdown(f"📅 **{selected_beach}**의 예상 운영 기간은 **{open_date}부터 {close_date}까지**입니다.")

        selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)

        # 🔄 session state 초기화
        if "show_result" not in st.session_state:
            st.session_state.show_result = False

        if st.button("🔍 예측 결과 보기"):
            st.session_state.show_result = True
            

        # 지도 시각화
        if not st.session_state.get("show_result"):
            st.markdown("### 🗺️ 2025년 전체 해수욕장 혼잡도 지도")

            latest_date = df["해수욕장일일일자"].max()
            base_df = df[df["해수욕장일일일자"] == latest_date]

            # ✅ 위도/경도 float으로 변환
            base_df["위도"] = pd.to_numeric(base_df["위도"], errors="coerce")
            base_df["경도"] = pd.to_numeric(base_df["경도"], errors="coerce")

            base_df = base_df.dropna(subset=["위도", "경도"])

            m = folium.Map(location=[base_df["위도"].mean(), base_df["경도"].mean()], zoom_start=7)
            congestion_color = {"여유": "green", "보통": "orange", "혼잡": "red"}

            for _, row in base_df.iterrows():
                folium.CircleMarker(
                    location=(row["위도"], row["경도"]),
                    radius=6,
                    color=congestion_color.get(row["예상 혼잡도"], "gray"),
                    fill=True,
                    fill_opacity=0.7,
                    popup=folium.Popup(
                        f"<b>{row['해수욕장이름']}</b><br>👥 {int(row['예상 방문자수'])}명<br>혼잡도: {row['예상 혼잡도']}",
                        max_width=200
                    )
                ).add_to(m)

            st_folium(m, use_container_width=True, height=600)


        # 🔍 예측 결과 출력
        if st.session_state.show_result:
            row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
            if not row.empty:
                visitors = int(row["예상 방문자수"].values[0])
                level = row["예상 혼잡도"].values[0]

                st.markdown(
                    f"<div class='result-card'><h4>📅 {selected_date} {selected_beach}의 예측 결과</h4><br>"
                    f"👥 예상 방문자수: <b>{visitors:,}명</b><br>"
                    f"🔵 예상 혼잡도: <b>{level}</b></div>",
                    unsafe_allow_html=True
                )

                # ✅ 여백 추가
                st.markdown("<br>", unsafe_allow_html=True)

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
                    df_to_show = alt.drop(columns=["위도", "경도"]).rename(columns={
                        "시/군/구": "시/군/구",
                        "해수욕장이름": "해수욕장",
                        "예상 방문자수": "예상 방문자수(명)",
                        "예상 혼잡도": "혼잡도"
                    })
                    st.dataframe(df_to_show, hide_index=True)

                with st.container():
                    st.markdown("<h3 style='text-align:left;'>🏖️ 같은 시/도 내 덜 혼잡한 해수욕장 위치 보기</h3>", unsafe_allow_html=True)

                    selected_loc = row[["위도", "경도"]].values[0]
                    m = folium.Map(location=selected_loc, zoom_start=10)
                    congestion_color = {"여유": "green", "보통": "orange"}

                    # 🔹 덜 혼잡한 해수욕장 마커
                    for _, r in alt.iterrows():
                        folium.CircleMarker(
                            location=(r["위도"], r["경도"]),
                            radius=8,
                            color=congestion_color.get(r["예상 혼잡도"], "gray"),
                            fill=True,
                            fill_opacity=0.7,
                            popup=folium.Popup(
                                f"<b>{r['해수욕장이름']}</b><br>👥 {int(r['예상 방문자수'])}명<br>혼잡도: {r['예상 혼잡도']}",
                                max_width=250
                            )
                        ).add_to(m)

                    # 🔵 선택한 해수욕장 파란 마커로 따로 표시
                    folium.CircleMarker(
                        location=(row["위도"].values[0], row["경도"].values[0]),
                        radius=10,
                        color="blue",
                        fill=True,
                        fill_opacity=1.0,
                        popup=folium.Popup(
                            f"<b>{row['해수욕장이름'].values[0]}</b><br>👥 {int(row['예상 방문자수'].values[0])}명<br>혼잡도: {row['예상 혼잡도'].values[0]}",
                            max_width=250
                        )
                    ).add_to(m)

                    st_folium(m, use_container_width=True, height=450)