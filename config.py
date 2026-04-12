# 설정 파일 - API 키와 위치 정보
import os

# ODSay API 설정
ODSAY_API_KEY = "KhvcwvGYKQWQx2oa4ceHk7RsPIjk8zeUNieX+t+cT0w"
ODSAY_BASE_URL = "https://api.odsay.com/v1/api/searchPubTransPathT"

# 위치 좌표
START_COORDS = (127.1493155, 37.5598741)  # 고덕래미안힐스테이트
END_COORDS = (127.1602946, 37.5499978)    # 강동고등학교

# WAQI API 설정 (미세먼지)
WAQI_TOKEN = "2ec0ef2e3aab752154e324e2fc1847a804e0fb2a"
WAQI_BASE_URL = "https://api.waqi.info/feed/geo:"

# 기상청 API 설정 (날씨)
WEATHER_SERVICE_KEY = "cN9NW1wAwTXgzCh7aPdgwZTons5JNB89mUqkP2P6sDtYYh%2Bc%2BAv3TJ0qq%2FQ2KwzdW5Li41upWP9jU1JimHoOtg%3D%3D"
WEATHER_BASE_URL = "http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getVilageFcst"
WEATHER_NX, WEATHER_NY = 37, 127  # 고덕동 격자 좌표