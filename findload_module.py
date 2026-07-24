import requests
import urllib.parse
import xml.etree.ElementTree as ET
from config import BUS_BASE_URL

def get_seoul_bus_arrival(service_key, ars_id, bus_route_nm):
    """ARS-ID(정류소 고유번호)를 사용하여 특정 버스의 도착 정보를 조회합니다."""
    decoded_key = urllib.parse.unquote(service_key)
    url = BUS_BASE_URL
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
            # XML 데이터를 파이썬이 이해할 수 있는 트리 구조(ElementTree)로 변환
            root = ET.fromstring(response.content) 
            
            # <itemList> 태그 하나하나가 버스 노선 정보를 담고 있음
            for item in root.findall(".//itemList"):
                rt_nm = item.findtext("rtNm") # 버스 번호 (예: 3412)
                if rt_nm == bus_route_nm:
                    # arrmsg1: 첫 번째 버스(예: 7분후), arrmsg2: 두 번째 버스(예: 15분후)
                    msg1 = item.findtext("arrmsg1") or "정보 없음"
                    msg2 = item.findtext("arrmsg2") or "정보 없음"
                    return f"{msg1} | {msg2}"
            return f"{bus_route_nm}번 버스 정보 없음"
    except Exception as e:
        print(f"서울 버스 API 조회 오류: {e}")
    return "정보를 가져올 수 없음"
