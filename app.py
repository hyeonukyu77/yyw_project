from datetime import datetime

import streamlit as st
from streamlit_js_eval import get_geolocation

from dust_module import get_dust_info
from location_module import get_neighborhood_name
from timetable_module import get_today_timetable
from weather_module import get_weather_emoji


st.set_page_config(
    page_title="아나비 - 아침 나의 비서",
    layout="wide",
    page_icon="🌤️",
)

st.markdown("<h1>ANAVI : 아침 나의 비서</h1>", unsafe_allow_html=True)
st.write(f"📅 날짜 : {datetime.now().strftime('%Y년 %m월 %d일')}")

location = get_geolocation(component_key="weather_geolocation")
latitude = None
longitude = None
if location and location.get("coords"):
    latitude = location["coords"].get("latitude")
    longitude = location["coords"].get("longitude")


@st.cache_data(ttl=3600, show_spinner=False)
def cached_neighborhood_name(lat, lon):
    return get_neighborhood_name(lat, lon)


neighborhood = cached_neighborhood_name(latitude, longitude)
location_label = neighborhood or ("현재 위치" if latitude is not None else "기본 위치")
st.subheader(f"🌤️ 날씨 요약 ({location_label})")

if latitude is not None and longitude is not None:
    st.caption("현재 위치를 기준으로 날씨와 미세먼지를 조회합니다.")
else:
    st.caption(
        "위치 권한을 허용하면 현재 위치의 날씨와 미세먼지를 보여드립니다. "
        "지금은 기본 위치를 사용합니다."
    )

weather_result = get_weather_emoji(latitude, longitude)
st.info(f"오늘의 전반적인 날씨는 **{weather_result}** 입니다.")

st.subheader("😷 미세먼지 현황")
dust_result = get_dust_info(latitude, longitude)
st.success(dust_result)

st.divider()
weekday_name, today_classes = get_today_timetable()
st.subheader(f"📚 오늘의 시간표 ({weekday_name})")

if today_classes:
    for item in today_classes:
        st.markdown(
            f"**{item['period']}교시 ({item['time']})** : "
            f"{item['subject']}"
        )
else:
    st.info("오늘은 등록된 수업이 없습니다.")
