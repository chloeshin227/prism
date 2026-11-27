"""홈 — 히어로, 스크롤 포커스 스토리, 진행 방식, 3D 프리즘, CTA"""
import streamlit as st
import streamlit.components.v1 as components

from core.ui import render, section_head, spacer, background_video
from data.market import ASSETS, RETURNS

st.markdown(
    """
    <style>
    @keyframes prismReveal {
        from {
            opacity: 0;
            transform: translateY(16px);
            filter: blur(5px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
            filter: blur(0);
        }
    }

    .hero-reveal {
        opacity: 0;
        animation: prismReveal 0.8s cubic-bezier(.2,.7,.2,1) forwards;
        will-change: transform, opacity;
    }

    .hero-reveal.delay-1 {
        animation-delay: 0.08s;
    }

    .hero-reveal.delay-2 {
        animation-delay: 0.22s;
    }

    .hero-reveal.delay-3 {
        animation-delay: 0.36s;
    }

    .hero-reveal.delay-4 {
        animation-delay: 0.50s;
    }

    .hero-reveal.delay-5 {
        animation-delay: 0.64s;
    }

    @media (prefers-reduced-motion: reduce) {
        .hero-reveal {
            opacity: 1;
            animation: none;
            transform: none;
            filter: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ── 0. 배경 영상 (assets/bg_light.mp4 · bg_dark.mp4가 있을 때만) ──
background_video(st.session_state.get("mono", False))

# ── 1. HERO ──────────────────────────────────────────────
tape = "".join(
    f'<span>{a["ticker"]} <b class="{"up" if RETURNS[0][a["id"]] >= 0 else "down"}">'
    f'{"▲" if RETURNS[0][a["id"]] >= 0 else "▼"}</b></span>'
    for a in ASSETS
)

render(
    f"""
    <section class="hero mm">
      <div class="eyebrow hero-reveal delay-1">
        <span class="stamp">Season 01</span>
        Investment Simulation Game
      </div>

      <div class="hero-title hero-reveal delay-2">
        Trade the market.<br>
        <span class="grad">Train the mind.</span>
      </div>

      <div class="hero-sub hero-reveal delay-3">
        <span> 가상의 1,000만 원으로 12개월을 투자해 보세요.
        <span>매달 뉴스와 지표를 읽고 직접 결정하면, 시장은 그 선택에 반응합니다.
        <span>게임이 끝나면 PRISM이 당신의 투자 습관을 비춰 드립니다.
      </div>

      <div class="ticker-tape hero-reveal delay-4">
        {tape}
      </div>
    </section>
    """
)

with st.container(key="hero_cta"):
    st.page_link("views/academy.py", label="Academy에서 시작하기  →")

render(
    '<div class="scroll-hint mm hero-reveal delay-5">'
    '<span></span>Scroll</div>'
)

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
    "투자의 적은 시장의 변동성이 아니라, 그 앞에서 흔들리는 우리의 심리입니다. 카드를 눌러 그 마음이 무엇인지 확인해 보세요.",
    center=True,
)
SLABS = [
    ("손실 회피", "Loss Aversion",
     "같은 크기라면 이익의 기쁨보다 손실의 아픔을 약 두 배 크게 느끼는 마음이에요. 그래서 떨어진 종목을 서둘러 팔아 버리거나, 손실을 확정하기 싫어 끝까지 붙들게 돼요.",
     "게임에서는 급락한 달에 겁이 나서 팔았는데, 바로 다음 달 시장이 반등하는 모습으로 나타나요."),
    ("군중 심리", "Herd · FOMO",
     "다들 사니까, 이미 오르고 있으니까 따라 사는 마음이에요. 기회를 놓칠까 두려운 FOMO가 더해지면, 가격이 크게 오른 뒤에 뒤늦게 사기 쉬워요.",
     "게임에서는 루머가 도는 종목이나 이미 많이 오른 종목을 뒤늦게 크게 사는 모습으로 나타나요."),
    ("확증 편향", "Confirmation",
     "내가 믿고 싶은 정보만 골라 보고, 반대되는 정보는 흘려 넘기는 마음이에요. 같은 기사 안에 경고가 있어도 좋은 소식만 기억해요.",
     "게임에서는 신고가 소식에 집중하다가, 같은 뉴스에 숨어 있던 경고를 놓치는 모습으로 나타나요."),
    ("과잉 확신", "Overconfidence",
     "내 판단이 틀릴 수 있다는 사실을 잊는 마음이에요. 확신이 클수록 한 종목에 크게 걸게 되고, 틀렸을 때는 회복하기 어려워요.",
     "게임에서는 한 자산에 비중 절반 이상을 몰아 넣는 모습으로 나타나요."),
]
# 카드를 누르면(포커스) 카드가 뒤집히며 뒷면에 뜻이 보임 — CSS만 사용(:focus)
render(
    '<div class="prism-wrap mm reveal"><div class="prism-row">'
    + "".join(
        f'<div class="slab" tabindex="0">'
        f'<div class="slab-in">'
        f'<div class="face front"><span class="lens"></span><b>{k}</b><i>{e}</i></div>'
        f'<div class="face back"><div class="kicker">{e}</div><div class="si-name">{k}</div>'
        f'<p>{d}</p><div class="si-game">→ {g}</div></div>'
        f'</div></div>'
        for k, e, d, g in SLABS
    )
    + "</div></div>"
)

components.html(
    "<script>(function(){var w=window.parent;if(w.__prismSlab){return;}w.__prismSlab=true;"
    "w.document.addEventListener('click',function(e){"
    "var s=e.target.closest&&e.target.closest('.slab');if(!s){return;}"
    "var wrap=s.closest('.prism-wrap');if(!wrap){return;}"
    "var i=s.getAttribute('data-i');"
    "wrap.setAttribute('data-open',wrap.getAttribute('data-open')===i?'':i);});})();</script>",
    height=0,
)

spacer(16)

# ── 5. CLOSING CTA ──────────────────────────────────────
render(
    """
    <div class="mm reveal center" style="text-align:center">
      <div class="kicker">Ready?</div>
      <div class="section-title">첫 번째 시장이<br><span class="grad">열립니다.</span></div>
      <div class="section-sub center" style="margin-bottom:0">한 판에 10–15분. 경제를 처음 공부하는 학생도 할 수 있도록 쉬운 말로 만들었어요.</div>
    </div>
    """
)
with st.container(key="end_cta"):
    st.page_link("views/academy.py", label="Academy 들어가기  →")
