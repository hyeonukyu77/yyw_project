# 아침도우미 서비스 통합 설정 파일

# 미세먼지 API 설정 (WAQI)
WAQI_TOKEN = "52f0a8f3dd29f06b1b76b47564458c40cdb5bff1"
WAQI_BASE_URL = "https://api.waqi.info/feed/geo:"
START_COORDS = (127.1493155, 37.5598741)  

# 기상청 API 설정 (단기예보)
WEATHER_SERVICE_KEY = "cN9NW1wAwTXgzCh7aPdgwZTons5JNB89mUqkP2P6sDtYYh%2Bc%2BAv3TJ0qq%2FQ2KwzdW5Li41upWP9jU1JimHoOtg%3D%3D"
WEATHER_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
WEATHER_NX, WEATHER_NY = 37, 127 