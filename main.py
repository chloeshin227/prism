"""
PRISM — Investment Simulator
배우고(Academy) → 직접 투자하고(Trading Floor) → 습관을 되돌아보는(Report) 교육용 투자 시뮬레이션 게임

이 파일이 앱의 '입구(entrypoint)'입니다.
Streamlit Cloud에 배포할 때 Main file path에 main.py 를 적어주세요.
"""
import streamlit as st

from core.theme import inject_theme
from core.ui import navbar, footer

# 1) 페이지 기본 설정 — 반드시 다른 st 명령보다 먼저 와야 합니다.
st.set_page_config(
    page_title="PRISM — Investment Simulator",
    page_icon="◆",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 2) monochrome(다크) 모드 상태 — 처음엔 OFF(라이트)
if "mono" not in st.session_state:
    st.session_state.mono = False

# 3) 페이지 등록 — views 폴더의 파일 하나가 페이지 하나
PAGES = [
    st.Page("views/home.py", title="Home", default=True),
    st.Page("views/academy.py", title="Academy"),
    st.Page("views/trade.py", title="Trade"),
    st.Page("views/report.py", title="Report"),
    st.Page("views/glossary_page.py", title="Glossary"),
]
# 기본 사이드바 메뉴는 숨기고(hidden) 직접 만든 유리 내비게이션 바를 씁니다.
current = st.navigation(PAGES, position="hidden")

# 4) 테마(CSS) 적용 → 상단 바 → 현재 페이지 실행 → 푸터
inject_theme(st.session_state.mono)
navbar(PAGES, current)
current.run()
footer()
