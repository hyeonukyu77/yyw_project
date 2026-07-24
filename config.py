# ANAVI(아나비) 서비스 통합 설정 파일

# 미세먼지 API 설정 (WAQI)
WAQI_TOKEN = "52f0a8f3dd29f06b1b76b47564458c40cdb5bff1"
WAQI_BASE_URL = "https://api.waqi.info/feed/geo:"
START_COORDS = (127.1493155, 37.5598741)  # 고덕래미안힐스테이트

# 기상청 API 설정 (단기예보)
WEATHER_SERVICE_KEY = "cN9NW1wAwTXgzCh7aPdgwZTons5JNB89mUqkP2P6sDtYYh%2Bc%2BAv3TJ0qq%2FQ2KwzdW5Li41upWP9jU1JimHoOtg%3D%3D"
WEATHER_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
WEATHER_NX, WEATHER_NY = 63, 126  # 위치 권한을 사용할 수 없을 때의 기본 격자

# 버스 정보 API 설정 (서울 열린데이터 광장)
BUS_BASE_URL = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"

# 알람 기준 설정: 학교/회사 목표 도착 시간
TARGET_ARRIVAL_TIME = "15:10"
