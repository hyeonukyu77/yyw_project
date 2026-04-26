import requests
import urllib.parse
import xml.etree.ElementTree as ET

def get_seoul_bus_arrival(service_key, ars_id, bus_route_nm):
    """ARS-ID(정류소 고유번호)를 사용하여 특정 버스의 도착 정보를 조회합니다."""
    decoded_key = urllib.parse.unquote(service_key)
    url = "http://ws.bus.go.kr/api/rest/stationinfo/getStationByUid"
    params = {
        "serviceKey": decoded_key,
        "arsId": ars_id
    }
    
    try:
        # 디버깅을 위한 전체 호출 URL 출력
        full_url = requests.Request('GET', url, params=params).prepare().url
        print(f"서울 버스 API 호출 URL: {full_url}")

        response = requests.get(url, params=params, timeout=5)
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            # XML 결과에서 모든 노선(itemList)을 순회하며 대상 버스 번호 확인
            for item in root.findall(".//itemList"):
                rt_nm = item.findtext("rtNm")
                if rt_nm == bus_route_nm:
                    # 첫 번째와 두 번째 도착 정보를 가져와 결합
                    msg1 = item.findtext("arrmsg1") or "정보 없음"
                    msg2 = item.findtext("arrmsg2") or "정보 없음"
                    return f"{msg1} | {msg2}"
            return f"{bus_route_nm}번 버스 정보 없음"
    except Exception as e:
        print(f"서울 버스 API 조회 오류: {e}")
    return "정보를 가져올 수 없음"
