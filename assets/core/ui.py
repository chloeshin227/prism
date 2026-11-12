"""
화면 곳곳에서 같이 쓰는 UI 도우미 함수 모음.
"""
import streamlit as st


def render(html: str) -> None:
    """HTML 조각을 화면에 그립니다.
    마크다운이 들여쓰기·빈 줄을 '코드 블록'으로 오해하지 않도록
    각 줄의 앞뒤 공백과 빈 줄을 정리한 뒤 출력합니다."""
    lines = [line.strip() for line in html.strip().splitlines() if line.strip()]
    st.markdown("\n".join(lines), unsafe_allow_html=True)


def toggle_mono() -> None:
    st.session_state.mono = not st.session_state.mono


def navbar(pages, current) -> None:
    """상단 고정 유리 내비게이션 바 + 우측 monochrome 버튼"""
    with st.container(key="navbar"):
        cols = st.columns([2.4, 0.9, 1.05, 0.9, 0.95, 1.05, 1.8], vertical_alignment="center")
        with cols[0]:
            render(
                '<div class="brand mm"><span class="brand-mark"></span>PRISM'
                '<span class="brand-sub">Investment Simulator</span></div>'
            )
        for i, (col, page) in enumerate(zip(cols[1:6], pages)):
            with col:
                with st.container(key=f"nav_{i}"):
                    st.page_link(page, label=page.title)
                if page.title == current.title:  # 현재 페이지 강조
                    render(
                        f"<style>.st-key-nav_{i} a{{background:var(--glass-strong)!important;"
                        f"box-shadow:inset 0 1px 0 var(--glass-highlight);}}"
                        f".st-key-nav_{i} a p{{color:var(--text)!important;}}</style>"
                    )
        with cols[6]:
            st.button("monochrome", key="mono_btn", on_click=toggle_mono)


def section_head(kicker: str, title: str, sub: str = "", center: bool = False) -> None:
    c = " center" if center else ""
    sub_html = f'<div class="section-sub{c}">{sub}</div>' if sub else ""
    render(
        f"""
        <div class="mm reveal{c}" style="margin-bottom:28px">
          <div class="kicker">{kicker}</div>
          <div class="section-title">{title}</div>
          {sub_html}
        </div>
        """
    )


def spacer(vh: float = 10) -> None:
    render(f'<div style="height:{vh}vh"></div>')


def won(v: float) -> str:
    """10000000 → ₩10,000,000"""
    return f"₩{v:,.0f}"


def pct(r: float, digits: int = 1) -> str:
    """0.123 → +12.3%"""
    return f"{r * 100:+.{digits}f}%"


def tone(r: float) -> str:
    """상승/하락/보합에 맞는 CSS 클래스 (한국식: 상승=붉은 계열, 하락=푸른 계열)"""
    if r > 0.0005:
        return "up"
    if r < -0.0005:
        return "down"
    return "flat"


def footer() -> None:
    render(
        """
        <div class="foot mm">
          <div>PRISM — Investment Simulator<br>Every decision leaves a lesson.</div>
          <div>모든 기업·시장·뉴스는 교육용으로 만든 가상의 시나리오입니다.<br>
          실제 투자 권유나 조언이 아닙니다.</div>
        </div>
        """
    )
