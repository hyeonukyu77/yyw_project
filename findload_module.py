import requests
from config import ODSAY_BASE_URL

TRANSPORT_NAMES = {
    1: "지하철",
    2: "버스",
    3: "도보",
}


def get_realtime_info(api_key, traffic_type, station_id, lane_name, way_code=None):
    """ODSay API를 사용하여 실시간 도착 정보를 조회합니다."""
    if not station_id or not lane_name:
        return "정보 없음"

    try:
        if traffic_type == 2:  # 버스
            url = "https://api.odsay.com/v1/api/busStationInfo"
            params = {"apiKey": api_key, "stationID": station_id}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                lanes = data.get("result", {}).get("lane", [])
                for lane in lanes:
                    # 버스 번호 매칭 (공백 제거 및 문자열 비교 강화)
                    if str(lane.get("busNo")).strip() == str(lane_name).strip():
                        arrival_sec = lane.get("arrival1Time")
                        if arrival_sec is not None:
                            if arrival_sec > 0:
                                return f"{arrival_sec // 60}분 {arrival_sec % 60}초 후 도착"
                            return "잠시 후 도착 예정"
        
        elif traffic_type == 1:  # 지하철
            url = "https://api.odsay.com/v1/api/subwayStationInfo"
            params = {"apiKey": api_key, "stationID": station_id}
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                realtime = data.get("result", {}).get("realtime", [])
                
                # 지하철 방향 매칭 (wayCode 1:상행/내선 -> upDownLine 0, 2:하행/외선 -> upDownLine 1)
                target_updown = (way_code - 1) if way_code in [1, 2] else None

                for rt in realtime:
                    rt_line = rt.get("subwayLineName", "")
                    rt_updown = rt.get("upDownLine")
                    
                    # 노선명과 방향(상/하행)이 일치하는지 확인
                    if (lane_name in rt_line or rt_line in lane_name) and (target_updown is None or rt_updown == target_updown):
                        arrival_msg = rt.get("arrivalMsg")
                        if arrival_msg:
                            return arrival_msg
    except Exception as e:
        print(f"실시간 정보 조회 오류: {e}")
    
    return "도착 정보 없음"


def get_odsay_route(api_key, sx, sy, ex, ey):
    """ODSay API로 출발지-도착지 경로를 조회합니다."""
    try:
        params = {
            "SX": sx,
            "SY": sy,
            "EX": ex,
            "EY": ey,
            "apiKey": api_key,
        }
        # 호출 URL 로그 출력
        full_url = requests.Request('GET', ODSAY_BASE_URL, params=params).prepare().url
        print(f"ODSay API 호출 URL: {full_url}")
        
        response = requests.get(ODSAY_BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "error" in data:
            error_messages = []
            for error in data.get("error", []):
                error_messages.append(error.get("message", str(error)))
            return None, "; ".join(error_messages), full_url

        result = data.get("result", {})
        paths = result.get("path", [])
        if not paths:
            return None, "경로를 찾을 수 없습니다.", full_url

        best_path = min(
            paths,
            key=lambda p: p.get("info", {}).get("totalTime", float("inf"))
        )

        # 모든 대중교통 수단(환승 포함)의 실시간 정보 조회
        for sub in best_path.get("subPath", []):
            traffic_type = sub.get("trafficType")
            if traffic_type in [1, 2]:  # 지하철 또는 버스
                station_id = sub.get("startID")
                lanes = sub.get("lane", [])
                lane_name = ""
                if lanes:
                    lane_name = lanes[0].get("busNo") or lanes[0].get("name")
                way_code = sub.get("wayCode")
                sub["realtime_info"] = get_realtime_info(api_key, traffic_type, station_id, lane_name, way_code)

        return best_path, None, full_url

    except requests.RequestException as exc:
        return None, f"네트워크 오류가 발생했습니다: {exc}", None
    except ValueError as exc:
        return None, f"응답 파싱에 실패했습니다: {exc}", None
    except Exception as exc:
        return None, f"경로 조회 중 오류가 발생했습니다: {exc}", None


def format_route_description(path):
    """ODSay 경로 결과를 사람이 읽기 좋은 텍스트로 변환합니다."""
    if not path:
        return ""

    info = path.get("info", {})
    total_time = info.get("totalTime")
    total_distance = info.get("totalDistance")
    payment = info.get("payment")
    station_count = info.get("stationCount")

    lines = []
    if total_time is not None:
        lines.append(f"**총 소요 시간:** {total_time}분")
    if total_distance is not None:
        lines.append(f"**총 거리:** {total_distance}m")
    if station_count is not None:
        lines.append(f"**정류장/역 수:** {station_count}개")
    if payment is not None:
        lines.append(f"**예상 요금:** {payment}원")

    sub_paths = path.get("subPath", [])
    if sub_paths:
        lines.append("\n**추천 경로:**")
        for idx, sub in enumerate(sub_paths, start=1):
            traffic_type = sub.get("trafficType") or sub.get("type")
            transport_name = TRANSPORT_NAMES.get(traffic_type, "이동")
            section_time = sub.get("sectionTime")
            distance = sub.get("distance")
            station_count = sub.get("stationCount")
            start_name = sub.get("startName")
            end_name = sub.get("endName")
            realtime_info = sub.get("realtime_info")
            lane = sub.get("lane", [])
            line_name = ""
            if isinstance(lane, list) and lane:
                line_name = lane[0].get("name") or lane[0].get("busNo") or lane[0].get("frontName", "")

            if transport_name == "도보":
                detail = f"{transport_name} {distance or 0}m, 약 {section_time or 0}분"
            else:
                if line_name:
                    detail = f"{transport_name} {line_name}, 약 {section_time or 0}분"
                else:
                    detail = f"{transport_name}, 약 {section_time or 0}분"
                if station_count is not None:
                    detail += f", {station_count}개 정류장"
            
            lines.append(f"{idx}. {detail}")

            if transport_name != "도보":
                if start_name:
                    lines.append(f"   ✅ **타는 곳:** {start_name}")
                if realtime_info:
                    lines.append(f"   ⏰ **도착 예정:** {realtime_info}")
                if end_name:
                    lines.append(f"   🏁 **내리는 곳:** {end_name}")

    return "\n".join(lines)
