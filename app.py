import streamlit as st
import re
from datetime import datetime, timedelta
from weather_module import get_weather_emoji
from dust_module import get_dust_info
from findload_module import get_seoul_bus_arrival
from config import WEATHER_SERVICE_KEY, TARGET_ARRIVAL_TIME

# 1. Streamlit 앱 설정
st.set_page_config(page_title="아나비 - 아침 나의 비서", layout="wide", page_icon="🌤️")

# 2. 알람 상태 초기화: config에 정의된 목표 시간(예: 10:30)을 로드
st.session_state.bus_alarm_time = TARGET_ARRIVAL_TIME
st.session_state.bus_alarm_active = True
if 'last_bus_alert_time' not in st.session_state:
    st.session_state.last_bus_alert_time = ""

st.markdown("<h1>ANAVI : 아침 나의 비서</h1>", unsafe_allow_html=True)
st.write(f"📅 **오늘의 정보:** {datetime.now().strftime('%Y년 %m월 %d일 %A')}")

# col1, col2 = st.columns(2)
# with col1:
st.subheader("🌤️ 날씨 요약")
weather_result = get_weather_emoji()
st.info(f"오늘의 전반적인 날씨는 **{weather_result}** 입니다.")
# st.markdown("---")
# with col2:
st.subheader("😷 미세먼지 현황")
dust_result = get_dust_info()
st.success(dust_result)

# st.markdown("---")

st.subheader(f"🗺️ {st.session_state.bus_alarm_time} 도착 목표 경로 (30초 자동 갱신)")

@st.fragment(run_every=30)
def display_integrated_info():
    # 1. 서울 버스 API를 통해 실시간 도착 정보 조회 (명일중학교 정류소, 3412번)
    bus_arrival = get_seoul_bus_arrival( 
        WEATHER_SERVICE_KEY, 
        "25176", 
        "3412"
    )
    
    # 역산 알람 로직 (목표 도착 시간 기준)
    if st.session_state.bus_alarm_active:
        try:
            # 목표 시간 객체 생성
            target_arrival_dt = datetime.strptime(st.session_state.bus_alarm_time, "%H:%M")
            
            # [계산] 필수 탑승 시각 = 목표 시간 - (버스 이동 10분 + 하차 후 도보 10분) = 20분 전
            required_boarding_dt = target_arrival_dt - timedelta(minutes=20)
            
            # 실시간 버스 정보에서 '분' 숫자만 추출 (예: "7분후" -> 7)
            minutes_match = re.search(r'(\d+)', bus_arrival) # "7분후"에서 7 추출
            if minutes_match:
                mins_to_bus = int(minutes_match.group(1))
                now = datetime.now()
                
                # 버스 정보를 로그에 출력 (디버깅용)
                print(f"[{now.strftime('%H:%M:%S')}] 버스 도착 예정: {mins_to_bus}분 후")

                # 버스가 정류장에 도착할 예상 시각
                estimated_bus_arrival_dt = now + timedelta(minutes=mins_to_bus)

                # [알람 조건 예시] 8시 등교 목표 시 7시 40분까지 버스를 타야 함 (이동 20분 소요).
                # 만약 현재 7시 33분이고 버스가 7분 뒤(7시 40분) 도착 예정이라면: "3412번 도착 7분 전입니다. 놓치면 지각입니다" 알람 발생.
                # 현재 정류장에 오는 버스가 딱 맞춰 타야 하는 버스인지 확인 (시:분 일치 여부)
                if estimated_bus_arrival_dt.strftime("%H:%M") == required_boarding_dt.strftime("%H:%M"):
                    current_time_str = now.strftime("%H:%M")
                    if st.session_state.last_bus_alert_time != current_time_str:
                        alert_msg = f"지금 오는 버스가 {mins_to_bus}분 뒤 도착합니다. 지금 타야 {st.session_state.bus_alarm_time}시 전에 도착합니다!"
                        st.toast(alert_msg, icon="🚌")
                        st.components.v1.html(f"""
                            <script>
                            // 알람 소리 재생
                            var audio = new Audio('https://actions.google.com/sounds/v1/alarms/beep_short.ogg');
                            audio.play();

                            if (window.Notification && Notification.permission === 'granted') {{
                                new Notification('🚌 지각 방지 알람', {{ body: '{alert_msg}' }});
                            }} else {{
                                console.log('알림 권한 없음');
                            }}
                            </script>
                        """, height=0)
                        st.session_state.last_bus_alert_time = current_time_str
        except Exception as e:
            pass

    # 2. 고정된 추천 경로 표시 (하드코딩)
    route_text = f"""
**총 소요 시간: 25분**

1. 도보 약 5분
2. 정류장 : 3412버스(명일중학교)
3. 도착 예정 : {bus_arrival}
4. 버스 이동 : 약 10분
5. 하차 : 한영중고
6. 도보 약 10분
    """
    st.markdown(f'<div class="route-container">{route_text}</div>', unsafe_allow_html=True)

display_integrated_info()