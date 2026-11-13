"""
테마(색상) 관리 파일.
- 색을 바꾸고 싶으면 아래 PALETTES 의 값만 바꾸면 사이트 전체가 바뀝니다.
- 실제 디자인 규칙(모양, 애니메이션)은 assets/style.css 에 있습니다.
"""
from pathlib import Path

import streamlit as st

CSS_PATH = Path(__file__).resolve().parent.parent / "assets" / "style.css"

PALETTES = {
    # ───────── monochrome OFF : 라이트 모드 ─────────
    # oat cream 배경 + mist blue 오브 + graphite 글자 + coral pink 포인트 + coffee blue 보조
    "light": {
        "bg": "#E9E5D6",            # oat cream
        "bg-2": "#F3F0E6",
        "text": "#222526",          # graphite
        "muted": "rgba(34,37,38,.62)",
        "faint": "rgba(34,37,38,.13)",
        "focus": "#222526",         # 스크롤 중앙에 온 글자 색
        "focus-glow": "none",
        "neon": "#2589D8",          # coffee blue
        "accent": "#FE6574",        # coral pink
        "accent-soft": "rgba(254,101,116,.14)",
        "accent-glow": "0 10px 30px rgba(254,101,116,.18)",
        "on-accent": "#222526",
        "irid-1": "#CCDCEF",        # mist blue
        "irid-2": "#FE6574",        # coral pink
        "irid-3": "#2589D8",        # coffee blue
        "irid-4": "#D9FFD2",        # tea green (무지갯빛 힌트)
        "orb-opacity": ".55",
        "glass": "rgba(255,255,255,.34)",
        "glass-strong": "rgba(255,255,255,.58)",
        "glass-border": "rgba(255,255,255,.75)",
        "glass-highlight": "rgba(255,255,255,.9)",
        "shadow": "0 24px 60px rgba(34,37,38,.10)",
        "brut-border": "#222526",
        "brut-shadow": "#222526",
        "rib-light": "rgba(255,255,255,.22)",
        "rib-dark": "rgba(34,37,38,.035)",
        "title-glow": "none",
        "grad": "linear-gradient(100deg,#222526 5%,#FE6574 55%,#2589D8 100%)",
        "mono-label": '"OFF"',
        "mono-chip-bg": "rgba(34,37,38,.08)",
        "mono-chip-fg": "#222526",
        "mono-chip-glow": "none",
    },
    # ───────── monochrome ON : 다크 모드 ─────────
    # charcoal black 주 배경 + royal blue 네온을 은은하게 + cherry-coke 핑크 포인트
    # (오렌지가 더 좋으면 accent 를 "#FE8500" 로 바꾸세요)
    "dark": {
        "bg": "#21232E",            # charcoal black
        "bg-2": "#181922",
        "text": "#F5F3F7",
        "muted": "rgba(245,243,247,.60)",
        "faint": "rgba(245,243,247,.14)",
        "focus": "#FFFFFF",
        "focus-glow": "0 0 32px rgba(16,91,255,.45)",
        "neon": "#105BFF",          # royal blue
        "accent": "#FF5C8A",        # cherry-coke pink
        "accent-soft": "rgba(255,92,138,.14)",
        "accent-glow": "0 0 28px rgba(255,92,138,.22)",
        "on-accent": "#14060A",
        "irid-1": "#105BFF",        # royal blue 네온
        "irid-2": "#651926",        # night bordeaux (체리 코크의 검붉은 톤)
        "irid-3": "#FF5C8A",        # pink
        "irid-4": "#75C3D1",        # sky blue (무지갯빛 힌트)
        "orb-opacity": ".42",
        "glass": "rgba(255,255,255,.045)",
        "glass-strong": "rgba(255,255,255,.085)",
        "glass-border": "rgba(255,255,255,.12)",
        "glass-highlight": "rgba(255,255,255,.16)",
        "shadow": "0 30px 80px rgba(0,0,0,.45)",
        "brut-border": "#0F0406",
        "brut-shadow": "#105BFF",
        "rib-light": "rgba(255,255,255,.03)",
        "rib-dark": "rgba(0,0,0,.16)",
        "title-glow": "0 0 40px rgba(16,91,255,.35)",
        "grad": "linear-gradient(100deg,#FFFFFF 5%,#FF5C8A 55%,#105BFF 100%)",
        "mono-label": '"ON"',
        "mono-chip-bg": "#105BFF",
        "mono-chip-fg": "#FFFFFF",
        "mono-chip-glow": "0 0 16px rgba(16,91,255,.85)",
    },
}


def inject_theme(mono: bool) -> None:
    """assets/style.css + 현재 모드의 색 변수를 페이지에 주입합니다."""
    palette = PALETTES["dark" if mono else "light"]
    variables = ":root{" + "".join(f"--{k}:{v};" for k, v in palette.items()) + "}"
    css = CSS_PATH.read_text(encoding="utf-8")
    st.markdown(f"<style>\n{css}\n{variables}\n</style>", unsafe_allow_html=True)
