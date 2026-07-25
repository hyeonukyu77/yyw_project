1. 주요 기능 구현 방법 및 API 정보
각 기능을 구현하기 위해 신뢰할 수 있는 공공 데이터와 외부 API를 연결해야 합니다.
날씨 및 미세먼지:
OpenWeatherMap API를 통해 현재 온도, 날씨 상태, 주간 예보 데이터를 가져올 수 있습니다.
국내 상세 데이터는 공공데이터포털(data.go.kr)의 '한국환경공단 에어코리아' API를 사용하여 근처 측정소의 미세먼지(PM10, PM2.5) 실시간 정보를 조회할 수 있습니다.
2. 추천 웹 프레임워크 및 디자인 가이드
디자인 감각이 없어도 깔끔한 결과물을 낼 수 있는 도구들입니다.
Streamlit (강력 추천):
특징: 복잡한 HTML/CSS 지식 없이 파이썬 코드만으로 대시보드 형태의 웹을 즉시 만들 수 있습니다.
디자인: 기본적으로 현대적이고 깔끔한 UI를 제공하며, st.metric으로 날씨 수치를 보여주거나 st.columns로 정보를 배치하여 전문적인 비서 화면을 구성하기 좋습니다.
3. 개발 로드맵 요약
환경 설정: 파이썬 설치 및 requests, streamlit (또는 flask) 라이브러리 설치.
데이터 수집: 날씨, 미세먼지 API 키를 발급받고 데이터를 파이싱하는 코드를 작성합니다.
UI 배치: 비서 앱의 메인 화면에 날씨 위젯 창을 배치합니다.

nodejs
vscode
python
(
pandas as pd
matplotlib.pyplot as plt
streamlit as st
)

execute >

python -m streamlit run app.py

c파일 빌드
cd C:\yyw_project
.\venv\Scripts\python.exe setup.py build_ext --inplace --force