import requests
import xml.etree.ElementTree as ET
from datetime import datetime
from config import WEATHER_SERVICE_KEY, WEATHER_NX, WEATHER_NY, WEATHER_BASE_URL

def get_weather_emoji():
    # 기상청 API 설정
    SERVICE_KEY = WEATHER_SERVICE_KEY
    NX, NY = WEATHER_NX, WEATHER_NY
    BASE_DATE = datetime.now().strftime("%Y%m%d")
    BASE_TIME = "0500"

    # API URL 구성
    URL = f"{WEATHER_BASE_URL}?serviceKey={SERVICE_KEY}&numOfRows=250&pageNo=1&base_date={BASE_DATE}&base_time={BASE_TIME}&nx={NX}&ny={NY}"

    try:
        # API에서 날씨 데이터 조회
        response = requests.get(URL, timeout=10)
        root = ET.fromstring(response.content)

        # XML 데이터 파싱
        weather_data = {}

        for item in root.iter("item"):
            fcst_date = item.find("fcstDate").text
            fcst_time = item.find("fcstTime").text
            category = item.find("category").text
            fcst_value = item.find("fcstValue").text

            key = f"{fcst_date}_{fcst_time}"

            if key not in weather_data:
                weather_data[key] = {}

            weather_data[key][category] = fcst_value

        # 5시~23시 동안의 날씨 데이터로 하루의 대표 날씨 결정
        snow_count = 0
        rain_count = 0
        cloudy_count = 0
        clear_count = 0

        for key in sorted(weather_data.keys()):
            fcst_date, fcst_time = key.split("_")
            date_obj = datetime.strptime(f"{fcst_date}{fcst_time}", "%Y%m%d%H%M")

            hour = date_obj.hour
            # 5시부터 23시까지만 분석
            if not (5 <= hour <= 23):
                continue

            # 강수형태 0(없음), 1(비), 2(비/눈), 3(눈), 4(소나기)
            pty = int(weather_data[key].get("PTY", 0))
            # 하늘상태 1(맑음), 3(구름많음), 4(흐림)
            sky = int(weather_data[key].get("SKY", 1))

            # 날씨별 개수 카운트
            if pty == 3:  # 눈
                snow_count += 1
            elif pty == 1 or pty == 4:  # 비 또는 소나기
                rain_count += 1
            elif sky == 4:  # 흐림
                cloudy_count += 1
            elif sky == 1:  # 맑음
                clear_count += 1

        # 하루의 대표 날씨 결정 (우선순위: 눈 > 비 > 구름 > 맑음)
        if snow_count > 0:
            today_weather = "❄️ 눈"
        elif rain_count > 0:
            today_weather = "☔ 비"
        elif cloudy_count > clear_count:
            today_weather = "☁️ 구름"
        else:
            today_weather = "☀️ 맑음"

        return today_weather

    except Exception as e:
        return f"❌ 오류: {str(e)}"