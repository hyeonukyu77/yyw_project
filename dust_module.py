import requests
import json
from config import WAQI_TOKEN, START_COORDS, WAQI_BASE_URL

def get_dust_info():
    # 고덕동 위치 기반 미세먼지 정보 조회
    LAT, LON = START_COORDS[1], START_COORDS[0]  # 위도, 경도 순서
    url = f"{WAQI_BASE_URL}{LAT};{LON}/?token={WAQI_TOKEN}"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        if data.get("status") != "ok":
            message = data.get("data") if isinstance(data.get("data"), str) else "미세먼지 정보를 가져오지 못했습니다."
            return f"⚠️ 고덕동 미세먼지 정보를 가져올 수 없습니다: {message}"

        station_name = data.get("data", {}).get("city", {}).get("name", "고덕동")
        iaqi = data.get("data", {}).get("iaqi", {})
        pm10_value = iaqi.get("pm10", {}).get("v")
        pm25_value = iaqi.get("pm25", {}).get("v")

        def dust_label(value, kind):
            if value is None:
                return "정보 없음"
            try:
                value = float(value)
            except Exception:
                return "정보 없음"

            if kind == "pm10":
                if value <= 30:
                    return "좋음"
                if value <= 80:
                    return "보통"
                if value <= 150:
                    return "나쁨"
                return "매우 나쁨"
            else:  # pm2.5
                if value <= 15:
                    return "좋음"
                if value <= 35:
                    return "보통"
                if value <= 75:
                    return "나쁨"
                return "매우 나쁨"

        def dust_face(label):
            return {
                "좋음": "😊",
                "보통": "😐",
                "나쁨": "😷",
                "매우 나쁨": "😖",
                "정보 없음": "❓",
            }.get(label, "❓")

        pm10_label = dust_label(pm10_value, 'pm10')
        pm25_label = dust_label(pm25_value, 'pm2_5')
        pm10_text = f"{dust_face(pm10_label)}({pm10_label})" if pm10_value is not None else "정보 없음"
        pm25_text = f"{dust_face(pm25_label)}({pm25_label})" if pm25_value is not None else "정보 없음"

        return f"미세먼지 {pm10_text}  |  초미세먼지 {pm25_text}"

    except Exception as e:
        return f"⚠️ 미세먼지 정보를 가져올 수 없습니다. {str(e)}"