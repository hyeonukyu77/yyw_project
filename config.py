# ANAVI(아나비) 서비스 통합 설정 파일

# 1. 위치 및 경로 좌표 설정
START_COORDS = (127.1493155, 37.5598741)  # 고덕래미안힐스테이트

# 2. 미세먼지 API 설정 (WAQI)
WAQI_TOKEN = "2ec0ef2e3aab752154e324e2fc1847a804e0fb2a"
WAQI_BASE_URL = "https://api.waqi.info/feed/geo:"

# 3. 기상청 API 설정 (단기예보)
WEATHER_SERVICE_KEY = "cN9NW1wAwTXgzCh7aPdgwZTons5JNB89mUqkP2P6sDtYYh%2Bc%2BAv3TJ0qq%2FQ2KwzdW5Li41upWP9jU1JimHoOtg%3D%3D"
WEATHER_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
WEATHER_NX, WEATHER_NY = 37, 127  # 고덕동 격자 좌표

# 4. 알람 기준 설정: 학교/회사 목표 도착 시간
TARGET_ARRIVAL_TIME = "14:40"