import requests
import xml.etree.ElementTree as ET
import math
from datetime import datetime, timedelta
from urllib.parse import unquote
from config import WEATHER_SERVICE_KEY, WEATHER_NX, WEATHER_NY, WEATHER_BASE_URL

def convert_to_grid(latitude, longitude):
    """
    브라우저의 GPS 좌표(위도·경도)를 기상청 격자 좌표(nx, ny)로 바꾼다.
    기상청 날씨 API는 위도·경도 대신 자체 격자 좌표를 사용하므로 이 변환이 필요하다.
    """
    earth_radius = 6371.00877
    grid_size = 5.0
    standard_parallel_1 = 30.0
    standard_parallel_2 = 60.0
    origin_longitude = 126.0
    origin_latitude = 38.0
    origin_x = 43.0
    origin_y = 136.0

    to_radians = math.pi / 180.0
    radius_per_grid = earth_radius / grid_size
    parallel_1 = standard_parallel_1 * to_radians
    parallel_2 = standard_parallel_2 * to_radians
    origin_lon = origin_longitude * to_radians
    origin_lat = origin_latitude * to_radians

    sn = math.tan(math.pi * 0.25 + parallel_2 * 0.5) / math.tan(
        math.pi * 0.25 + parallel_1 * 0.5
    )
    sn = math.log(math.cos(parallel_1) / math.cos(parallel_2)) / math.log(sn)
    sf = math.tan(math.pi * 0.25 + parallel_1 * 0.5)
    sf = math.pow(sf, sn) * math.cos(parallel_1) / sn
    ro = math.tan(math.pi * 0.25 + origin_lat * 0.5)
    ro = radius_per_grid * sf / math.pow(ro, sn)

    ra = math.tan(math.pi * 0.25 + latitude * to_radians * 0.5)
    ra = radius_per_grid * sf / math.pow(ra, sn)
    theta = longitude * to_radians - origin_lon
    if theta > math.pi:
        theta -= 2.0 * math.pi
    if theta < -math.pi:
        theta += 2.0 * math.pi
    theta *= sn

    nx = int(ra * math.sin(theta) + origin_x + 0.5)
    ny = int(ro - ra * math.cos(theta) + origin_y + 0.5)
    return nx, ny


def get_weather_emoji(latitude=None, longitude=None):
    # 기상청 API 설정
    SERVICE_KEY = WEATHER_SERVICE_KEY
    if latitude is not None and longitude is not None:
        NX, NY = convert_to_grid(float(latitude), float(longitude))
    else:
        NX, NY = WEATHER_NX, WEATHER_NY
    now = datetime.now()
    # 단기예보는 02, 05, 08, 11, 14, 17, 20, 23시에 발표되며
    # API에는 발표 약 10분 뒤부터 안정적으로 제공된다.
    available_times = (2, 5, 8, 11, 14, 17, 20, 23)
    candidates = [
        now.replace(hour=hour, minute=10, second=0, microsecond=0)
        for hour in available_times
    ]
    available = [candidate for candidate in candidates if candidate <= now]
    base_datetime = max(available) if available else (
        now - timedelta(days=1)
    ).replace(hour=23, minute=10, second=0, microsecond=0)
    BASE_DATE = base_datetime.strftime("%Y%m%d")
    BASE_TIME = base_datetime.strftime("%H00")

    # API URL 구성
    try:
        # API에서 날씨 데이터 조회
        response = requests.get(
            WEATHER_BASE_URL,
            params={
                "serviceKey": unquote(SERVICE_KEY),
                "numOfRows": 1000,
                "pageNo": 1,
                "dataType": "XML",
                "base_date": BASE_DATE,
                "base_time": BASE_TIME,
                "nx": NX,
                "ny": NY,
            },
            timeout=10,
        )
        response.raise_for_status()
        root = ET.fromstring(response.content)

        result_code = root.findtext(".//resultCode")
        if result_code != "00":
            result_message = root.findtext(".//resultMsg") or "알 수 없는 API 오류"
            return f"⚠️ 날씨 정보를 가져올 수 없습니다. ({result_message})"

        # XML 데이터 파싱
        weather_data = {}

        for item in root.iter("item"):
            fcst_date = item.findtext("fcstDate")
            fcst_time = item.findtext("fcstTime")
            category = item.findtext("category")
            fcst_value = item.findtext("fcstValue")
            if not all((fcst_date, fcst_time, category, fcst_value)):
                continue

            key = f"{fcst_date}_{fcst_time}"

            if key not in weather_data:
                weather_data[key] = {}

            weather_data[key][category] = fcst_value

        if not weather_data:
            return "⚠️ 제공된 날씨 예보가 없습니다."

        # 오늘 5시~23시 동안의 데이터로 하루의 대표 날씨 결정
        snow_count = 0
        rain_count = 0
        cloudy_count = 0
        clear_count = 0

        for key in sorted(weather_data.keys()):
            fcst_date, fcst_time = key.split("_")
            if fcst_date != now.strftime("%Y%m%d"):
                continue
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

    except (requests.RequestException, ET.ParseError, TypeError, ValueError):
        return "⚠️ 날씨 정보를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요."
