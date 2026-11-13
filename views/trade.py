"""Trading Floor — 매달 뉴스·지표를 보고 비중을 정하면 한 달이 흐르는 시뮬레이션"""
from html import escape

import streamlit as st

from core.charts import line_chart, sparkline
from core.game import get_game, advance, reset_game, total, is_over
from core.ui import render, section_head, spacer, won, pct, tone
from data.market import ASSETS, MONTHS, RETURNS, PRICES, BENCH, START_CASH

ss = st.session_state
ss.setdefault("unlocked", False)
g = get_game()
T = len(MONTHS)


def skip_lessons():
    ss.unlocked = True


render('<div class="page-head"></div>')

# ── 0. 잠금 화면 ────────────────────────────────────────
if not ss.unlocked:
    render(
        """
        <div class="glass mm" style="text-align:center;padding:60px 30px">
          <span class="stamp">Locked</span>
          <div class="section-title" style="margin-top:18px">아직 시장이 열리지 않았어요.</div>
          <div class="section-sub center">Academy에서 카드 5장을 읽고 퀴즈를 통과하면 Trading Floor가 열립니다.</div>
        </div>
        """
    )
    spacer(3)
    with st.container(key="end_cta"):
        st.page_link("views/academy.py", label="Academy로 가기  →")
    spacer(2)
    c = st.columns([1, 1, 1])[1]
    with c:
        st.button("학습 건너뛰고 바로 시작", on_click=skip_lessons)
    st.stop()

# ── 1. 게임 종료 화면 ───────────────────────────────────
if is_over(g):
    final = total(g)
    render(
        f"""
        <div class="glass mm" style="text-align:center;padding:60px 30px">
          <span class="stamp">Market Closed</span>
          <div class="section-title" style="margin-top:18px">12개월이 끝났습니다.</div>
          <div class="big-value num" style="margin:10px 0">{won(final)}</div>
          <div class="delta {tone(final / START_CASH - 1)}">{pct(final / START_CASH - 1)}</div>
          <div class="section-sub center" style="margin-top:16px">이제 Report에서 나의 투자 습관을 확인해 보세요.</div>
        </div>
        """
    )
    spacer(3)
    with st.container(key="end_cta"):
        st.page_link("views/report.py", label="Report 보기  →")
    spacer(2)
    c = st.columns([1, 1, 1])[1]
    with c:
        st.button("↺  새 게임 시작", on_click=reset_game)
    st.stop()

# ── 2. 대시보드 ─────────────────────────────────────────
m = g["turn"]
month = MONTHS[m]
now = total(g)
ret = now / START_CASH - 1

render(
    f"""
    <div class="dash-top mm">
      <div>
        <div class="kicker">Trading Floor</div>
        <div class="month-pill" style="margin-top:10px"><b class="num">{m + 1:02d}</b><span>/ {T} · {month['label']}</span></div>
      </div>
      <div style="text-align:right">
        <div class="label" style="margin:0 0 6px">Total Assets</div>
        <div class="big-value num">{won(now)}</div>
        <div class="delta {tone(ret)} num">{pct(ret)} <span class="muted">since start</span></div>
      </div>
    </div>
    """
)
spacer(3)

left, right = st.columns([1.6, 1], gap="medium")
with left:
    chart = line_chart(
        [(BENCH[: m + 1], "var(--muted)", False), (g["values"], "var(--accent)", True)],
        height=210, uid="pf",
    )
    render(
        f"""
        <div class="glass mm">
          <div class="label">Portfolio vs Benchmark</div>
          {chart}
          <div class="legend"><span><i style="background:var(--accent)"></i>My portfolio</span>
          <span><i style="background:var(--muted)"></i>Benchmark</span></div>
        </div>
        """
    )
with right:
    mood = month["mood"]
    mood_txt = "극단적 공포" if mood < 25 else "공포" if mood < 45 else "중립" if mood < 60 else "탐욕" if mood < 75 else "극단적 탐욕"
    render(
        f"""
        <div class="glass mm">
          <div class="label">Market Indicators</div>
          <div class="ind">
            <div><span>기준금리</span><b class="num">{month['rate']:.2f}%</b></div>
            <div><span>물가상승률</span><b class="num">{month['cpi']:.1f}%</b></div>
            <div><span>투자 심리</span><b class="num">{mood}</b></div>
          </div>
          <div class="gauge">
            <div class="track"><div class="dot" style="left:{mood}%"></div></div>
            <div class="ends"><span>Fear</span><span>{mood_txt}</span><span>Greed</span></div>
          </div>
        </div>
        """
    )

spacer(5)

# ── 3. 이번 달 뉴스 ─────────────────────────────────────
render(
    f"""
    <div class="news mm reveal">
      <span class="stamp">Breaking · {month['label']}</span>
      <div class="headline">{escape(month['headline'])}</div>
      <div class="body">{escape(month['body'])}</div>
    </div>
    """
)

# 지난달 결과
if m > 0:
    last = RETURNS[m - 1]
    chips = "".join(
        f'<span class="chip" style="margin:0 8px 8px 0">{a["ticker"]}&nbsp;<b class="{tone(last[a["id"]])}">{pct(last[a["id"]])}</b></span>'
        for a in ASSETS
    )
    prev_ret = g["values"][-1] / g["values"][-2] - 1
    render(
        f"""
        <div class="glass tight mm" style="margin-top:22px">
          <div class="label">Last month · {MONTHS[m - 1]['label']} — 내 포트폴리오 <b class="{tone(prev_ret)}">{pct(prev_ret)}</b></div>
          <div>{chips}</div>
          <div class="muted" style="font-size:.88rem;margin-top:6px;line-height:1.6">{escape(MONTHS[m - 1]['after'])}</div>
        </div>
        """
    )

spacer(7)

# ── 4. 종목 카드 ────────────────────────────────────────
section_head("Market", "오늘의 종목", "모든 기업은 가상의 기업입니다. 가격 흐름과 설명을 보고 판단해 보세요.")
cards = []
for a in ASSETS:
    pid = a["id"]
    hist = PRICES[pid][: m + 1]
    r = RETURNS[m - 1][pid] if m > 0 else 0.0
    held = g["hold"][pid]
    cards.append(
        f"""<div class="glass tight lift asset">
        <div class="row1"><span class="nm">{a['name']}</span><span class="chip">{a['ticker']}</span></div>
        <div class="row1"><span class="px num">₩{hist[-1]:,.0f}</span><span class="rt {tone(r)} num">{pct(r) if m > 0 else '—'}</span></div>
        {sparkline(hist, a['color'], uid=pid)}
        <div class="row1" style="margin-top:4px"><span class="chip">{a['sector']}</span><span class="chip">Risk · {a['risk']}</span></div>
        <div class="ds">{escape(a['desc'])}</div>
        <div class="ds">보유 <b class="num">{won(held)}</b></div></div>"""
    )
render('<div class="grid small mm">' + "".join(cards) + "</div>")

spacer(8)

# ── 5. 비중 정하기 ──────────────────────────────────────
section_head(
    "Your Move",
    f"{month['label']}의 포트폴리오",
    "각 자산에 전체 자산의 몇 %를 담을지 정하세요. 남는 비율은 현금(월 0.25% 이자)으로 남습니다. 비중을 바꾸면 사고판 금액의 0.2%가 거래 비용으로 나가요.",
)
targets = {}
with st.container(key="alloc"):
    cols = st.columns(2, gap="large")
    for i, a in enumerate(ASSETS):
        with cols[i % 2]:
            targets[a["id"]] = st.slider(
                f"{a['name']}  ·  {a['ticker']}",
                min_value=0, max_value=100, step=5,
                value=int(g["targets"][a["id"]]),
                format="%d%%",
            )

used = sum(targets.values())
cash_pct = 100 - used
over = used > 100
bar = "".join(
    f'<i style="width:{targets[a["id"]] / max(used, 100) * 100:.2f}%;background:{a["color"]}"></i>' for a in ASSETS
)
status = f"100%를 넘었어요 ({used}%)" if over else f"투자 {used}%  ·  현금 {cash_pct}%"
render(
    f"""
    <div class="mm" style="margin-top:18px">
      <div class="alloc-total{' over' if over else ''}"><span>Allocation</span><span class="num {'up' if over else ''}">{status}</span></div>
      <div class="alloc-bar">{bar}</div>
    </div>
    """
)
spacer(3)
with st.container(key="commit"):
    st.button(
        f"{month['label']} 확정  →  한 달 보내기" if not over else "비중 합계를 100% 이하로 맞춰 주세요",
        type="primary",
        disabled=over,
        on_click=advance,
        args=(targets,),
    )
