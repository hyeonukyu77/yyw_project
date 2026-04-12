import streamlit as st
from weather_module import get_weather_emoji
from dust_module import get_dust_info
from alarm_module import alarm_ui
from findload_module import get_odsay_route, format_route_description
from config import ODSAY_API_KEY, START_COORDS, END_COORDS, ODSAY_BASE_URL

st.title("아침 나의 비서")

st.markdown("---")

# 날씨 정보 표시
with st.spinner("날씨 정보를 가져오는 중..."):
    weather_result = get_weather_emoji()
    st.markdown(f"<h3>{weather_result}</h3>", unsafe_allow_html=True)

st.markdown("---")

# 미세먼지 정보 표시
with st.spinner("미세먼지 정보를 가져오는 중..."):
    dust_result = get_dust_info()
    st.markdown(f"<h3>{dust_result}</h3>", unsafe_allow_html=True)

# 추천 대중교통 길찾기
# 호출 URL 표시
odsay_url = f"{ODSAY_BASE_URL}?SX={START_COORDS[0]}&SY={START_COORDS[1]}&EX={END_COORDS[0]}&EY={END_COORDS[1]}&apiKey={ODSAY_API_KEY}"
#st.info(f"🔗 ODSay API 호출 URL: {odsay_url}")

with st.spinner("추천 경로를 조회하는 중..."):
    route, error, actual_url = get_odsay_route(
        ODSAY_API_KEY,
        START_COORDS[0],
        START_COORDS[1],
        END_COORDS[0],
        END_COORDS[1],
    )
    # if actual_url:
    #     st.info(f"✅ 실제 호출 URL: {actual_url}")

st.markdown("---")
st.subheader("🗺️ 추천 길찾기 정보")
if error:
    st.error(error)
else:
    st.markdown(format_route_description(route))

# 알람 UI
st.markdown("---")
st.subheader("🔔 알람 설정")
alarm_ui()