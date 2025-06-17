import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

# 페이지 기본 설정
st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="centered")

# 스타일 설정
st.markdown("""
    <style>
    .stApp {
        background: linear-gradient(to bottom, #a2d4f7, #e0f7fa);
        font-family: 'Helvetica', sans-serif;
        padding: 0 5vw;
    }
    </style>
""", unsafe_allow_html=True)

# 데이터 로딩 함수
@st.cache_data
def load_data():
    df = pd.read_csv("2025_해수욕장_예측결과_최종.csv")
    df["해수욕장일일일자"] = pd.to_datetime(df["해수욕장일일일자"])
    return df

df = load_data()

# 제목
st.markdown("<h1 style='text-align: center;'>🌊 혼잡한 바다는 <span style='color:#114BFA'>SEA</span>러!</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</p>", unsafe_allow_html=True)

# 시/도 선택
selected_sido = st.selectbox("🏞️ 시/도를 선택하세요", sorted(df["시/도"].unique()))
filtered_sido_df = df[df["시/도"] == selected_sido]

# 시/군/구 선택
selected_sigungu = st.selectbox("🏙️ 시/군/구를 선택하세요", sorted(filtered_sido_df["시/군/구"].unique()))
filtered_region_df = filtered_sido_df[filtered_sido_df["시/군/구"] == selected_sigungu]

# 해수욕장 선택
selected_beach = st.selectbox("📍 해수욕장을 선택하세요", sorted(filtered_region_df["해수욕장이름"].unique()))
filtered_beach_df = filtered_region_df[filtered_region_df["해수욕장이름"] == selected_beach]

# 날짜 선택
selected_date = st.date_input("📅 방문 날짜를 선택하세요", value=pd.to_datetime("2025-06-01"))

# 예측 결과 확인
if st.button("🔍 예상 방문자수 보기"):
    result = filtered_beach_df[filtered_beach_df["해수욕장일일일자"] == pd.to_datetime(selected_date)]

    if not result.empty:
        visitors = int(result["예상 방문자수"].values[0])
        congestion = result["예상 혼잡도"].values[0]

        st.markdown(f"""
        <div style="background-color:#ffffffdd;padding:20px;border-radius:10px;box-shadow:0 4px 8px rgba(0,0,0,0.1);margin-top:20px;">
            <h3>📅 {selected_date.strftime('%Y-%m-%d')} {selected_beach}의 예측 결과</h3>
            <p>👥 <b>예상 방문자수:</b> {visitors:,}명</p>
            <p>📍 <b>예상 혼잡도:</b> {congestion}</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.warning("선택한 날짜에 해당하는 예측 데이터가 없습니다. 다른 날짜를 선택해주세요.")

# ✅ 선택한 날짜 기준 전국 혼잡도 지도 시각화
st.markdown("### 🗺️ 전국 해수욕장 혼잡도 지도")

selected_day_data = df[df["해수욕장일일일자"] == pd.to_datetime(selected_date)]

if not selected_day_data.empty:
    try:
        map_center = [selected_day_data["위도"].astype(float).mean(), selected_day_data["경도"].astype(float).mean()]
    except Exception:
        map_center = [36.5, 127.5]  # fallback center
    
    m = folium.Map(location=map_center, zoom_start=7)

    for _, row in selected_day_data.iterrows():
        color = {
            "여유": "green",
            "보통": "orange",
            "혼잡": "red"
        }.get(row["예상 혼잡도"], "blue")

        folium.CircleMarker(
            location=(row["위도"], row["경도"]),
            radius=6,
            popup=folium.Popup(f"{row['해수욕장이름']}<br>예상 방문자수: {row['예상 방문자수']}명<br>혼잡도: {row['예상 혼잡도']}", max_width=250),
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    # 범례
    legend_html = """
     <div style="position: fixed; 
                 bottom: 50px; left: 50px; width: 160px; height: 120px; 
                 border:2px solid grey; z-index:9999; font-size:14px;
                 background-color:white; padding:10px;">
     <b>🟢 혼잡도 범례</b><br>
     <span style='color:green;'>● 여유</span><br>
     <span style='color:orange;'>● 보통</span><br>
     <span style='color:red;'>● 혼잡</span>
     </div>
     """
    m.get_root().html.add_child(folium.Element(legend_html))

    st_folium(m, width=700, height=500)
else:
    st.info("선택한 날짜에 해당하는 전국 해수욕장 데이터가 없습니다.")
