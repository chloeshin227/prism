"""Trading Floor — 시나리오를 고르고, 매달 뉴스·이벤트를 보고 비중을 정하면 한 달이 흐르는 시뮬레이션"""
from html import escape

import streamlit as st
import streamlit.components.v1 as components

from core.charts import line_chart, sparkline
from core.game import (get_game, advance, reset_game, choose_scenario, sc, total, is_over,
                       event_for, limits_for, answer_event, finalize)
from core.progress import profile, xp_strip_html
from core.ui import render, section_head, spacer, won, pct, tone
from data.events import STOCKS
from data.market import ASSETS, ASSET_MAP, IDS, START_CASH
from data.scenarios import SCENARIOS, SCENARIO_ORDER

ss = st.session_state
ss.setdefault("unlocked", False)
g = get_game()


def skip_lessons():
    ss.unlocked = True

def commit_month(targets):
    """한 달 보내기 → 다음 화면은 맨 위부터 보이도록 표시"""
    advance(targets)
    ss.scroll_top = True


def scroll_top():
    """화면이 새로 그려진 뒤 맨 위로 부드럽게 올라가기.
    스크립트 내용이 매번 똑같으면 Streamlit이 같은 요소로 보고 다시 실행하지 않으므로,
    호출할 때마다 번호(nonce)를 바꿔서 매번 새로 실행되게 한다."""
    ss.scroll_n = ss.get("scroll_n", 0) + 1
    components.html(
        "<script>/*" + str(ss.scroll_n) + "*/function up(){var d=window.parent.document;"
        "var m=d.querySelector('[data-testid=\"stMain\"]');"
        "if(m){m.scrollTo({top:0,behavior:'smooth'});}"
        "d.documentElement.scrollTo({top:0,behavior:'smooth'});}"
        "setTimeout(up,300);setTimeout(up,900);</script>",
        height=0,
    )

def effect_text(o):
    """이벤트 보기가 만드는 제한을 한 줄로"""
    parts = []
    if o["max"] and all(o["max"].get(a) == 0 for a in STOCKS):
        parts.append("주식 비중 0% 고정")
    elif o["max"] and len(o["max"]) == len(IDS) and len(set(o["max"].values())) == 1:
        parts.append(f"한 자산 최대 {next(iter(o['max'].values()))}%")
    else:
        parts += [f"{ASSET_MAP[a]['ticker']} 최대 {v}%" for a, v in o["max"].items()]
    parts += [f"{ASSET_MAP[a]['ticker']} 최소 {v}%" for a, v in o["min"].items()]
    if o["cash_min"]:
        parts.append(f"현금 최소 {o['cash_min']}%")
    return " · ".join(parts)

if ss.pop("scroll_top", False):
    scroll_top()

render('<div class="page-head"></div>')
render(xp_strip_html())

spacer(2)

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
    with st.container(key="center_btn"):
        st.button("학습 건너뛰고 바로 시작", on_click=skip_lessons)
    st.stop()

# ── 1. 시나리오 고르기 ──────────────────────────────────
if g["sid"] is None:
    section_head(
        "Choose your market",
        "어떤 시장에서<br>시작할까요?",
        "같은 기업, 다른 1년. 시장마다 성격과 함정이 달라요. 한 번 시작하면 12개월 동안 이 시장이 이어집니다.",
    )
    done = profile()["scenarios_done"]
    cols = st.columns(3, gap="medium")
    for col, sid in zip(cols, SCENARIO_ORDER):
        S = SCENARIOS[sid]
        with col:
            stars = "★" * S["level"] + "☆" * (3 - S["level"])
            learn = "".join(f'<span class="chip">{escape(x)}</span>' for x in S["learn"])
            mark = '<span class="verdict ok">Cleared</span>' if sid in done else ""
            render(
                f"""
                <div class="glass lift scn mm">
                  <div class="scn-top"><span class="scn-lv">{stars}</span>{mark}</div>
                  <div class="scn-name">{S['name']}</div>
                  <div class="scn-en">{S['en']}</div>
                  <div class="scn-line">{escape(S['tagline'])}</div>
                  <div class="scn-learn">{learn}</div>
                </div>
                """
            )
            st.button("이 시장으로 시작  →", key=f"pick_{sid}", type="primary",
                      on_click=choose_scenario, args=(sid,), use_container_width=True)
    st.stop()

S = sc(g)
MONTHS, RETURNS, PRICES, BENCH = S["months"], S["returns"], S["prices"], S["bench"]
T = len(MONTHS)

# ── 2. 게임 종료 화면 ───────────────────────────────────
if is_over(g):
    finalize(g)
    final = total(g)
    render(
        f"""
        <div class="glass mm" style="text-align:center;padding:60px 30px">
          <span class="stamp">Market Closed · {S['name']}</span>
          <div class="section-title" style="margin-top:18px">12개월이 끝났습니다.</div>
          <div class="big-value num" style="margin:10px 0">{won(final)}</div>
          <div class="delta {tone(final / START_CASH - 1)}">{pct(final / START_CASH - 1)}</div>
          <div class="section-sub center" style="margin-top:16px">이제 Report에서 나의 투자 캐릭터와 습관을 확인해 보세요.</div>
        </div>
        """
    )
    spacer(3)
    with st.container(key="end_cta"):
        st.page_link("views/report.py", label="Report 보기  →")
    spacer(2)
    with st.container(key="center_btn"):
        st.button("↺  새 게임 시작 (시장 다시 고르기)", on_click=reset_game)
    st.stop()

# ── 3. 대시보드 ─────────────────────────────────────────
m = g["turn"]
month = MONTHS[m]
now = total(g)
ret = now / START_CASH - 1
if m > 0:
    prev_total = g["values"][-2]
    mom = now / prev_total - 1
    diff = now - prev_total
    mom_html = (f'<div class="delta {tone(mom)} num" style="margin-top:4px">전월 대비 {"+" if diff >= 0 else "-"}{won(abs(diff))} ({pct(mom)})</div>')
else:
    mom_html = ""
  
render(
    f"""
    <div class="dash-top mm">
      <div>
        <div class="kicker">Trading Floor · {S['name']}</div>
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

# ── 4. 이번 달 뉴스 ─────────────────────────────────────
render(
    f"""
    <div class="news mm reveal">
      <span class="stamp">Breaking · {month['label']}</span>
      <div class="headline">{escape(month['headline'])}</div>
      <div class="body">{escape(month['body'])}</div>
    </div>
    """
)

# ── 5. 돌발 이벤트 카드 ─────────────────────────────────
ev = event_for(g, m)
choice_i = g["events"].get(m)
pending = ev is not None and choice_i is None
if ev is not None:
    spacer(2)
    if pending:
        render(
            f"""
            <div class="event mm">
              <span class="stamp hot">Event</span>
              <div class="ev-title">{escape(ev['title'])}</div>
              <div class="ev-body">{escape(ev['body'])}</div>
              <div class="ev-hint">선택하면 이번 달 비중에 실제로 영향을 줘요.</div>
            </div>
            """
        )
        with st.container(key="evbtn"):
            bcols = st.columns(len(ev["options"]), gap="medium")
            for i, o in enumerate(ev["options"]):
                with bcols[i]:
                    st.button(o["label"], key=f"ev_{g['gid']}_{m}_{i}", on_click=answer_event,
                              args=(m, i), use_container_width=True)
    else:
        o = ev["options"][choice_i]
        eff = effect_text(o)
        eff_html = f'<div class="ev-effect">적용 · {escape(eff)}</div>' if eff else ""
        render(
            f"""
            <div class="event done mm">
              <span class="stamp">Event · {escape(ev['title'])}</span>
              <div class="ev-pick">나의 선택 — {escape(o['label'])}</div>
              <div class="ev-body">{escape(o['result'])}</div>
              {eff_html}
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

# ── 6. 종목 카드 ────────────────────────────────────────
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
render('<div class="grid assets mm">' + "".join(cards) + "</div>")
spacer(8)

spacer(6) 

# ── 7. 비중 정하기 ──────────────────────────────────────
section_head(
    "Your Move",
    f"{month['label']}의 포트폴리오",
    "각 자산에 전체 자산의 몇 %를 담을지 정하세요. 남는 비율은 현금(월 0.25% 이자)으로 남습니다. 비중을 바꾸면 사고판 금액의 0.2%가 거래 비용으로 나가요.",
)
mins, maxs, cash_min = limits_for(g, m)
if ev is not None and not pending:
    eff = effect_text(ev["options"][choice_i])
    if eff:
        render(f'<div class="mm" style="margin-bottom:14px;padding-left:28px"><span class="stamp hot">이벤트 적용</span>&nbsp;&nbsp;<b>{escape(eff)}</b></div>')

targets = {}
with st.container(key="alloc"):
    cols = st.columns(2, gap="large")
    for i, a in enumerate(ASSETS):
        lo, hi = mins.get(a["id"], 0), maxs.get(a["id"], 100)
        label = f"{a['name']}  ·  {a['ticker']}"
        with cols[i % 2]:
            if hi <= lo:
                targets[a["id"]] = lo
                st.slider(label, 0, 100, value=lo, step=5, format="%d%%", disabled=True, key=f"fix_{g['gid']}_{m}_{a['id']}")
            else:
                default = min(max(int(g["targets"][a["id"]]), lo), hi)
                targets[a["id"]] = st.slider(label, min_value=lo, max_value=hi, step=5, value=default, format="%d%%")

used = sum(targets.values())
limit = 100 - cash_min
cash_pct = 100 - used
over = used > limit
bar = "".join(
    f'<i style="width:{targets[a["id"]] / max(used, 100) * 100:.2f}%;background:{a["color"]}"></i>' for a in ASSETS
)
if over:
    status = f"투자 한도 {limit}%를 넘었어요 ({used}%)"
else:
    status = f"투자 {used}%  ·  현금 {cash_pct}%"
render(
    f"""
    <div class="mm" style="margin-top:18px">
      <div class="alloc-total{' over' if over else ''}"><span>Allocation</span><span class="num {'up' if over else ''}">{status}</span></div>
      <div class="alloc-bar">{bar}</div>
    </div>
    """
)
spacer(3)
if pending:
    btn_label = "먼저 위의 돌발 상황에 답해 주세요"
elif over:
    btn_label = f"비중 합계를 {limit}% 이하로 맞춰 주세요"
else:
    btn_label = f"{month['label']} 확정  →  한 달 보내기"
with st.container(key="commit"):
    st.button(btn_label, type="primary", disabled=over or pending, on_click=commit_month, args=(targets,))
