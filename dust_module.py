import requests
from config import WAQI_TOKEN, START_COORDS, WAQI_BASE_URL

def get_dust_info(latitude=None, longitude=None):
    """현재 좌표 또는 기본 좌표의 실시간 미세먼지 정보를 가져온다."""
    if latitude is not None and longitude is not None:
        lat, lon = float(latitude), float(longitude)
    else:
        lon, lat = START_COORDS

    url = f"{WAQI_BASE_URL}{lat};{lon}/?token={WAQI_TOKEN}"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()

        # 1. API 응답 상태 확인
        if data.get("status") != "ok":
            # 에러 메시지가 문자열이면 보여주고, 아니면 기본 문구 출력 (방어적 코드)
            error_detail = data.get("data")
            message = error_detail if isinstance(error_detail, str) else "데이터 형식이 올바르지 않습니다."
            return f"⚠️ 현재 위치의 미세먼지 정보를 가져올 수 없습니다: {message}"

        # 2. 데이터 추출 (iaqi: Individual Air Quality Index)
        iaqi = data.get("data", {}).get("iaqi", {})
        pm10_value = iaqi.get("pm10", {}).get("v") # 미세먼지 수치
        pm25_value = iaqi.get("pm25", {}).get("v") # 초미세먼지 수치

        # 3. 수치를 사람이 읽기 좋은 글자로 변환하는 내부 함수
        def get_status_text(value, kind):
            if value is None: return "정보 없음", "❓"
            val = float(value)
            
            # 기준치 설정 (미세먼지 vs 초미세먼지)
            if kind == "pm10":
                limits = [30, 80, 150]
            else: # pm2.5
                limits = [15, 35, 75]
                
            if val <= limits[0]: return "좋음", "😊"
            if val <= limits[1]: return "보통", "😐"
            if val <= limits[2]: return "나쁨", "😷"
            return "매우 나쁨", "😖"

        # 4. 최종 결과 조립
        p10_label, p10_emoji = get_status_text(pm10_value, "pm10")
        p25_label, p25_emoji = get_status_text(pm25_value, "pm25")

        return f"미세먼지 {p10_emoji}({p10_label}) | 초미세먼지 {p25_emoji}({p25_label})"

    except (requests.RequestException, ValueError, TypeError):
        return "⚠️ 미세먼지 정보를 가져올 수 없습니다. 잠시 후 다시 시도해 주세요."
