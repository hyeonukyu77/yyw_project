import streamlit as st
import streamlit.components.v1 as components

def alarm_ui():
    # 세션 상태 초기화
    if 'alarm_set' not in st.session_state:
        st.session_state.alarm_set = False
    if 'alarm_hour' not in st.session_state:
        st.session_state.alarm_hour = 6
    if 'alarm_minute' not in st.session_state:
        st.session_state.alarm_minute = 0

    # 시간/분 선택 및 설정/취소 버튼
    col1, col2, col3, col4 = st.columns([1, 1, 0.3, 1])
    with col1:
        st.session_state.alarm_hour = st.selectbox("시간", range(0, 24), index=st.session_state.alarm_hour)
    with col2:
        st.session_state.alarm_minute = st.selectbox("분", range(0, 60, 5), index=st.session_state.alarm_minute // 5)
    with col3:
        if st.button("설정"):
            st.session_state.alarm_set = True
            alarm_script1 = f"""
            <script>
                const notification = new Notification('🔔 알람!', {{
                    body: '알람이 설정되었습니다: {st.session_state.alarm_hour:02d}:{st.session_state.alarm_minute:02d}',
                }});
            </script>
            """
            components.html(alarm_script1, height=0)
    with col4:
        if st.button("취소"):
            st.session_state.alarm_set = False
            alarm_script2 = f"""
            <script>
                const notification = new Notification('🔔 알람!', {{
                    body: '알람이 취소되었습니다: {st.session_state.alarm_hour:02d}:{st.session_state.alarm_minute:02d}',
                }});
            </script>
            """
            components.html(alarm_script2, height=0)

    # JavaScript 알람 (브라우저에서 시간 체크)
    if st.session_state.alarm_set:
        alarm_time = f"{st.session_state.alarm_hour:02d}:{st.session_state.alarm_minute:02d}"

        # 브라우저의 JavaScript로 실시간 알람 구현
        alarm_script = f"""
        <script>
        // 알람 상태 저장 (중복 울림 방지)
        let alarm_played = false;
        let audio_context = null;
        let current_oscillators = [];
        let alarm_interval = null;

        function stop_alarm() {{
            // 현재 울리고 있는 소리 중지
            if (alarm_interval) {{
                clearInterval(alarm_interval);
                alarm_interval = null;
            }}
            current_oscillators.forEach(osc => {{
                try {{
                    osc.stop();
                }} catch(e) {{}}
            }});
            current_oscillators = [];
            if (audio_context) {{
                audio_context.close();
                audio_context = null;
            }}
        }}

        function play_alarm_sound() {{
            if (!audio_context) {{
                audio_context = new (window.AudioContext || window.webkitAudioContext)();
            }}

            const oscillator = audio_context.createOscillator();
            const gainNode = audio_context.createGain();

            oscillator.connect(gainNode);
            gainNode.connect(audio_context.destination);

            oscillator.frequency.value = 1000;
            oscillator.type = 'sine';

            gainNode.gain.setValueAtTime(0.5, audio_context.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audio_context.currentTime + 0.5);

            oscillator.start(audio_context.currentTime);
            oscillator.stop(audio_context.currentTime + 0.5);
            current_oscillators.push(oscillator);
        }}

        // 매초 시간 확인
        setInterval(function() {{
            const now = new Date();
            const current_time =
                String(now.getHours()).padStart(2, '0') + ':' +
                String(now.getMinutes()).padStart(2, '0');

            const alarm_time = '{alarm_time}';

            // 알람 시간이 되면
            if (current_time === alarm_time && !alarm_played) {{
                alarm_played = true;

                // 알람 소리를 1초마다 반복해서 울림
                alarm_interval = setInterval(function() {{
                    play_alarm_sound();
                }}, 1000);

                // 브라우저 알림
                if ('Notification' in window) {{
                    if (Notification.permission === 'granted') {{
                        const notification = new Notification('🔔 알람!', {{
                            body: '{alarm_time}입니다. (닫기 버튼으로 소리 중지)',
                            icon: 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text y=".9em" font-size="90">🔔</text></svg>',
                            requireInteraction: true
                        }});

                        // 알림 닫기 이벤트에서 소리 중지
                        notification.onclose = function() {{
                            stop_alarm();
                        }};

                        // 알림 클릭 이벤트에서도 소리 중지
                        notification.onclick = function() {{
                            stop_alarm();
                            notification.close();
                        }};
                    }} else {{
                        // 알림 권한이 없으면 콘솔에 로그 출력
                        console.log('알림 권한이 없습니다. 브라우저 설정에서 알림을 허용해주세요.');
                        // 권한 요청 시도
                        Notification.requestPermission().then(function(permission) {{
                            if (permission === 'granted') {{
                                console.log('알림 권한이 허용되었습니다.');
                            }}
                        }});
                    }}
                }}
            }}

            // 다음 분이 되면 상태 리셋 (예: 10:30에서 10:31로 바뀌면)
            const next_minute = String((parseInt(alarm_time.split(':')[1]) + 1) % 60).padStart(2, '0');
            const next_time = alarm_time.split(':')[0] + ':' + next_minute;
            if (current_time === next_time) {{
                alarm_played = false;
            }}
        }}, 1000);

        // 브라우저 알림 권한 요청
        if ('Notification' in window && Notification.permission === 'default') {{
            Notification.requestPermission();
        }}
        </script>
        """

        components.html(alarm_script, height=0)