"""홈 — 히어로, 스크롤 포커스 스토리, 진행 방식, 3D 프리즘, CTA"""
import streamlit as st

from core.ui import render, section_head, spacer
from data.market import ASSETS, RETURNS

# ── 1. HERO ──────────────────────────────────────────────
tape = "".join(
    f'<span>{a["ticker"]} <b class="{"up" if RETURNS[0][a["id"]] >= 0 else "down"}">'
    f'{"▲" if RETURNS[0][a["id"]] >= 0 else "▼"}</b></span>'
    for a in ASSETS
)
render(
    f"""
    <section class="hero mm">
      <div class="eyebrow"><span class="stamp">Season 01</span>Investment Simulation Game</div>
      <div class="hero-title">Trade the market.<br><span class="grad">Train the mind.</span></div>
      <div class="hero-sub">
        가상의 1,000만 원으로 12개월을 투자해 보세요.
        매달 뉴스와 지표를 읽고 직접 결정하면, 시장은 그 선택에 반응합니다.
        게임이 끝나면 PRISM이 당신의 투자 습관을 비춰 드립니다.
      </div>
      <div class="ticker-tape">{tape}</div>
    </section>
    """
)
with st.container(key="hero_cta"):
    st.page_link("views/academy.py", label="Academy에서 시작하기  →")
render('<div class="scroll-hint mm"><span></span>Scroll</div>')

# ── 2. SCROLL STORY (화면 중앙 줄만 선명해지는 효과) ─────────
STORY = [
    "시장은 매일 소리칩니다.",
    "지금 사라, 당장 팔아라.",
    "그런데 대부분의 손실은",
    "시장이 아니라 마음에서 시작됩니다.",
    "PRISM은 그 마음을 훈련합니다.",
    "당신의 첫 1,000만 원.<small>Every decision leaves a lesson.</small>",
]
render(
    '<section class="story mm">'
    + "".join(f'<div class="story-line">{line}</div>' for line in STORY)
    + "</section>"
)

# ── 3. HOW IT WORKS ─────────────────────────────────────
section_head(
    "How it works",
    "배우고, 결정하고,<br>되돌아봅니다.",
    "읽기만 하는 경제 공부는 쉽게 잊힙니다. PRISM은 직접 결정하고, 결과를 겪고, 그 이유를 되짚는 과정으로 배웁니다.",
)
FEATURES = [
    ("01", "Academy", "분산 투자, 금리, 투자 심리 같은 핵심 개념을 카드 5장으로 배우고, 퀴즈를 통과하면 시장이 열립니다."),
    ("02", "Trading Floor", "매달 뉴스·금리·물가·투자 심리 지수를 보고 7개 자산의 비중을 정하세요. 한 턴이 지나면 한 달이 흐릅니다."),
    ("03", "Report", "수익률, 최대 낙폭, 벤치마크 비교와 함께 군중 심리·공포 매도·확증 편향 같은 나의 투자 습관을 분석합니다."),
]
render(
    '<div class="grid mm reveal">'
    + "".join(
        f'<div class="glass lift feature"><div class="icon-orb"></div>'
        f'<div class="no">{n}</div><div class="t">{t}</div><div class="d">{d}</div></div>'
        for n, t, d in FEATURES
    )
    + "</div>"
)

spacer(14)

# ── 4. 3D PRISM ─────────────────────────────────────────
section_head(
    "Behavioral Finance",
    "당신을 흔드는<br>네 개의 마음.",
    "투자의 적은 시장의 변동성이 아니라, 그 앞에서 흔들리는 우리의 심리입니다. 카드 위에 마우스를 올려보세요.",
    center=True,
)
SLABS = [("손실 회피", "Loss Aversion"), ("군중 심리", "Herd · FOMO"), ("확증 편향", "Confirmation"), ("과잉 확신", "Overconfidence")]
render(
    '<div class="prism-wrap mm reveal"><div class="prism-row">'
    + "".join(f'<div class="slab"><span class="lens"></span><b>{k}</b><i>{e}</i></div>' for k, e in SLABS)
    + '<div class="beam"></div></div></div>'
)

spacer(16)

# ── 5. CLOSING CTA ──────────────────────────────────────
render(
    """
    <div class="mm reveal center" style="text-align:center">
      <div class="kicker">Ready?</div>
      <div class="section-title">첫 번째 시장이<br><span class="grad">열립니다.</span></div>
      <div class="section-sub center" style="margin-bottom:30px">한 판에 10–15분. 경제를 처음 공부하는 학생도 할 수 있도록 쉬운 말로 만들었어요.</div>
    </div>
    """
)
with st.container(key="end_cta"):
    st.page_link("views/academy.py", label="Academy 들어가기  →")
