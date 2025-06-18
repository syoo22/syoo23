import streamlit as st
import pandas as pd
import numpy as np
from datetime import date
import folium
from folium import CircleMarker
from streamlit_folium import st_folium
from folium import Popup

# 1️⃣ 페이지 기본 설정 ─────────────────────────────────────────────
st.set_page_config(page_title="혼잡한 바다는 SEA러!", layout="wide")

# 2️⃣ CSS 스타일 + 제목/부제목/설명 ──────────────────────────────
st.markdown("""
<style>
/* ✅ 기본 배경 및 글꼴 스타일 */
.stApp {
    background: linear-gradient(to bottom, #a6d9f7, #e4f8ff);
    font-family: 'Segoe UI', sans-serif;
    font-size: 16px;
    padding-top: 6vh !important;
    padding-left: 5vw;
    padding-right: 5vw;
    padding-bottom: 0;
}

/* ✅ 제목 & 부제목 */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: 800;
    color: #003366;
    margin-bottom: 0.2em;
}
.title .blue {
    color: #0066ff;
}
.subtitle {
    text-align: center;
    font-size: 17px;
    color: #004080;
    margin-bottom: 0.8em;
}
.description {
    text-align: center;
    font-size: 14px;
    color: #333333;
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
        padding-top: 6vh !important;
        padding-left: 3vw !important;
        padding-right: 3vw !important;
    }
    .title {
        font-size: 28px !important;
    }
    .subtitle {
        font-size: 14px !important;
    }
    .description {
        font-size: 12px !important;
    }
    .result-card {
        font-size: 14px !important;
        padding: 16px !important;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🌊 혼잡한 바다는 <span class="blue">SEA</span>러!</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">해수욕장과 날짜를 선택하면 예상 방문자수와 혼잡도를 알려드려요!</div>', unsafe_allow_html=True)
st.markdown('<div class="description">이 서비스는 여름철 <b>해수욕장 혼잡 문제</b>를 해결하기 위한 <b>공공 예측 서비스</b>입니다.</div>', unsafe_allow_html=True)

# 👇 나머지 데이터 로딩부터 예측, 지도 코드 등은 여기에 붙이면 됩니다.