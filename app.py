import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import folium
from folium import CircleMarker
from streamlit_folium import st_folium
import branca.colormap as cm
from folium import Popup

# 1️⃣ 페이지 기본 설정 ─────────────────────────────────────────────
st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="wide")

# 2️⃣ CSS 스타일 + 제목/부제목/설명 통합 ──────────────────────────────
st.markdown("""
<style>
/* ✅ 기본 배경 및 글꼴 스타일 */
.stApp {
    background: linear-gradient(to bottom, #a6d9f7, #e4f8ff);
    font-family: 'Segoe UI', sans-serif;
    font-size: 16px;
    padding: 0 5vw;
}

/* ✅ 제목 & 부제목 */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    color: #003366;
}
.title .blue {
    color: #0066ff;
}
.subtitle {
    text-align: center;
    font-size: 17px;
    color: #004080;
    margin-bottom: 2rem;
}

/* ✅ 예측 결과 카드 */
.result-card {
    background: #ffffffdd;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    max-width: 600px;
    margin: 20px auto;
}

/* ✅ 지도 iframe 여백 제거 */
iframe {
    display: block;
    margin: 0 auto;
    padding: 0 !important;
}
.folium-map {
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
}

/* ✅ 모바일 반응형 대응 */
@media screen and (max-width: 600px) {
    .stApp {
        font-size: 13px !important;
        padding: 0 3vw !important;
    }
    .title {
        font-size: 28px !important;
    }
    .subtitle {
        font-size: 14px !important;
    }
    .result-card {
        font-size: 14px !important;
        padding: 16px !important;
    }
}
</style>
""", unsafe_allow_html=True)



# 3️⃣ 데이터 로딩 ─────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("beach_prediction_2025.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# 4️⃣ 지역별 선택 리스트 구성 ─────────────────────────────────────
sido_list = sorted(df["시/도"].dropna().unique())
sigungu_dict = {
    sido: sorted(df[df["시/도"] == sido]["시/군/구"].dropna().unique())
    for sido in sido_list
}
beach_dict = {
    (sido, sigungu): sorted(df[(df["시/도"] == sido) & (df["시/군/구"] == sigungu)]["해수욕장이름"].dropna().unique())
    for sido in sido_list for sigungu in sigungu_dict[sido]
}

# 5️⃣ 사용자 입력 UI ──────────────────────────────────────────────
selected_sido = st.selectbox("📌 시/도를 선택하세요", sido_list)
sigungu_options = sigungu_dict.get(selected_sido, [])
selected_sigungu = st.selectbox("🏞️ 시/군/구를 선택하세요", sigungu_options)
beach_options = beach_dict.get((selected_sido, selected_sigungu), [])

if beach_options:
    selected_beach = st.selectbox("🏖️ 해수욕장을 선택하세요", beach_options)
else:
    selected_beach = None
    st.warning("선택한 시/군/구에 등록된 해수욕장이 없습니다.")

if selected_beach:
    beach_dates = df[df["해수욕장이름"] == selected_beach]["해수욕장일일일자"]
    open_date, close_date = beach_dates.min().date(), beach_dates.max().date()
    st.markdown(f"📅 **{selected_beach}** 운영 기간: **{open_date} ~ {close_date}**")
    selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=open_date, min_value=open_date, max_value=close_date)
else:
    selected_date = None

# 6️⃣ 예측 결과 & 추천 출력 ──────────────────────────────────────
if st.button("🔍 예측 결과 보기") and selected_beach and selected_date:
    row = df[(df["해수욕장이름"] == selected_beach) & (df["해수욕장일일일자"] == pd.to_datetime(selected_date))]
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

# 7️⃣ 혼잡도 지도 시각화 ─────────────────────────────────────────

# ✅ 페이지 하단 여백 제거
st.markdown("""
<style>
.block-container {
    padding-bottom: 0rem !important;
}
</style>
""", unsafe_allow_html=True)

st.markdown("---")
st.subheader("📍 2025년 예상 방문자수 기반 혼잡도 지도")

# ✅ 지도 필터용 시/도 리스트
sido_list_for_map = sorted(df["시/도"].dropna().unique())

# ✅ 사용자 필터 선택
st.markdown("#### 🗺️ 지도에 표시할 지역 선택")
selected_map_sido = st.selectbox("지도에 표시할 시/도 선택", ["전체"] + sido_list_for_map)

# ✅ 해수욕장별 평균 혼잡도 데이터
df_grouped = df.groupby(['해수욕장이름', '위도', '경도'], as_index=False).agg({
    '예상 방문자수': 'sum',
    '예상 혼잡도': lambda x: x.mode()[0] if not x.mode().empty else "정보 없음"
})
df_grouped['위도'] = pd.to_numeric(df_grouped['위도'], errors='coerce')
df_grouped['경도'] = pd.to_numeric(df_grouped['경도'], errors='coerce')

# ✅ 지도에 표시할 데이터 필터링
if selected_map_sido == "전체":
    map_df = df_grouped.copy()
else:
    allowed_beaches = df[df["시/도"] == selected_map_sido]["해수욕장이름"].unique()
    map_df = df_grouped[df_grouped["해수욕장이름"].isin(allowed_beaches)]

# ✅ 지도 중심 설정
center_lat = map_df['위도'].mean()
center_lon = map_df['경도'].mean()
m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

# ✅ 혼잡도 → 색상
def get_color_by_congestion(level):
    if level == "여유":
        return "green"
    elif level == "보통":
        return "orange"
    elif level == "혼잡":
        return "red"
    else:
        return "gray"

# ✅ 마커 추가
for _, row in map_df.iterrows():
    color = get_color_by_congestion(row["예상 혼잡도"])
    
    popup_html = f"""
    <div style="width:260px; word-break:keep-all;">
        <b>{row['해수욕장이름']}</b>
        <table style="margin-top:5px; width:100%; table-layout:fixed; border-collapse:collapse;">
            <colgroup>
                <col style="width:55%;">
                <col style="width:45%;">
            </colgroup>
            <tr>
                <td style="white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
                    👥 예상 방문자수
                </td>
                <td style="text-align:right; white-space:nowrap;">
                    {int(row['예상 방문자수']):,}명
                </td>
            </tr>
            <tr>
                <td style="white-space:nowrap;">🚦 혼잡도</td>
                <td style="text-align:right;"><b>{row['예상 혼잡도']}</b></td>
            </tr>
        </table>
    </div>
    """

    folium.CircleMarker(
        location=[row['위도'], row['경도']],
        radius=7,
        color=color,
        fill=True,
        fill_opacity=0.7,
        popup=folium.Popup(popup_html, max_width=280)  # ← 여기도 260~280으로 약간 늘려줘
    ).add_to(m)


# ✅ 요약 문구 출력
beach_count = map_df['해수욕장이름'].nunique()
st.markdown(f"✅ 현재 지도에는 **{beach_count}개 해수욕장**이 표시되어 있습니다.")

# ✅ 여백 제거 스타일
st.markdown("""
<style>
iframe {
    display: block;
    margin: 0 auto;
    padding: 0 !important;
}
.folium-map {
    margin: 0 !important;
    padding: 0 !important;
    height: auto !important;
}
</style>
""", unsafe_allow_html=True)

# ✅ 지도 출력 (정수 높이로 수정)
st_folium(m, width="100%", height=600, returned_objects=[])