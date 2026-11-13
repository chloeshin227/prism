"""Report — 성과 분석 + 투자 습관(행동 편향) 디브리핑"""
from html import escape

import streamlit as st

from core.charts import line_chart
from core.game import get_game, reset_game, metrics, detect_biases, is_over
from core.ui import render, section_head, spacer, won, pct, tone
from data.market import ASSET_MAP, MONTHS, BENCH

g = get_game()
T = len(MONTHS)

render('<div class="page-head"></div>')
section_head("Report", "나의 투자 리포트", "숫자는 결과를, 습관은 이유를 말해 줍니다.")

# ── 아직 기록이 없을 때 ─────────────────────────────────
if not g["history"]:
    render(
        """
        <div class="glass mm" style="text-align:center;padding:56px 30px">
          <div class="section-title" style="font-size:2rem">아직 투자 기록이 없어요.</div>
          <div class="section-sub center">Trading Floor에서 첫 달을 시작해 보세요.</div>
        </div>
        """
    )
    spacer(3)
    with st.container(key="end_cta"):
        st.page_link("views/trade.py", label="Trading Floor로 가기  →")
    st.stop()

if not is_over(g):
    render(
        f'<div class="glass tight mm" style="margin-bottom:22px"><span class="stamp">In progress</span>'
        f'&nbsp;&nbsp;<b>{g["turn"]} / {T}개월</b> 진행 중이에요. 지금까지의 기록으로 분석한 중간 리포트입니다.</div>'
    )

# ── 1. 등급 + 핵심 지표 ─────────────────────────────────
k = metrics(g)
c1, c2 = st.columns([1, 2.6], gap="large")
with c1:
    render(f'<div class="score-box mm"><b>{k["grade"]}</b><span>Investor grade</span></div>')
with c2:
    stats = [
        (won(k["final"]), "Final assets", ""),
        (pct(k["ret"]), "My return", tone(k["ret"])),
        (pct(k["bench"]), "Benchmark", tone(k["bench"])),
        (f"-{k['mdd'] * 100:.1f}%", "Max drawdown", "down" if k["mdd"] > 0 else ""),
        (won(k["fees"]), "Fees paid", ""),
    ]
    render(
        '<div class="grid small mm">'
        + "".join(f'<div class="glass tight stat"><b class="num {c}">{v}</b><span>{lbl}</span></div>' for v, lbl, c in stats)
        + "</div>"
    )

spacer(4)
chart = line_chart(
    [(BENCH[: g["turn"] + 1], "var(--muted)", False), (g["values"], "var(--accent)", True)],
    height=240, uid="rp",
)
render(
    f"""
    <div class="glass mm">
      <div class="label">12 months — 나 vs 벤치마크</div>
      {chart}
      <div class="legend"><span><i style="background:var(--accent)"></i>My portfolio</span>
      <span><i style="background:var(--muted)"></i>Benchmark (7개 자산 균등 보유)</span></div>
    </div>
    """
)

# ── 2. 투자 습관 분석 ───────────────────────────────────
spacer(10)
section_head("Behavior", "PRISM이 비춰 본<br>나의 투자 습관", "결정 기록을 바탕으로 자주 나타나는 행동 편향과 잘한 점을 찾았어요.")
biases = detect_biases(g)
if not biases:
    render('<div class="glass mm">눈에 띄는 편향이 발견되지 않았어요. 균형 잡힌 투자였어요!</div>')
else:
    cards = []
    for b in biases:
        badge = '<span class="verdict ok">Strength</span>' if b["kind"] == "good" else '<span class="verdict bad">Watch out</span>'
        when = " · ".join(MONTHS[x]["label"] for x in b["months"])
        when_html = f'<span class="chip">{when}</span>' if when else ""
        cards.append(
            f'<div class="glass lift bias"><div class="bias-head">{badge}{when_html}</div>'
            f'<div class="bias-name">{b["name"]}</div><div class="bias-en">{b["en"]}</div>'
            f'<div class="bias-text">{escape(b["text"])}</div><div class="bias-tip">→ {escape(b["tip"])}</div></div>'
        )
    render('<div class="grid mm">' + "".join(cards) + "</div>")

# ── 3. 월별 타임라인 (나의 결정 다시 보기) ─────────────────
spacer(10)
section_head("Replay", "열두 달, 다시 보기")
flag_months = {x for b in biases if b["kind"] == "warn" for x in b["months"]}
items = []
for h in g["history"]:
    mo = h["month"]
    r = h["end"] / h["start"] - 1
    top = sorted(((w, a) for a, w in h["targets"].items() if w > 0), reverse=True)[:3]
    picks = ", ".join(f"{ASSET_MAP[a]['name']} {w}%" for w, a in top) or "전액 현금"
    crit = " critical" if (r <= -0.05 or mo in flag_months) else ""
    items.append(
        f'<div class="tl-item{crit}"><div class="tl-time">{MONTHS[mo]["label"]} · <span class="{tone(r)}">{pct(r)}</span></div>'
        f'<div class="tl-text">{escape(MONTHS[mo]["headline"])}</div>'
        f'<div class="tl-sub">나의 선택: {picks}</div>'
        f'<div class="tl-sub">{escape(MONTHS[mo]["after"])}</div></div>'
    )
render(f'<div class="glass mm"><div class="timeline">{"".join(items)}</div></div>')

# ── 4. 핵심 정리 ────────────────────────────────────────
spacer(8)
POINTS = [
    "분산 투자는 '많이' 담는 것이 아니라 '다르게 움직이는 것'을 담는 것이다.",
    "근거 없는 루머와 급등은 늦게 탈수록 위험하다.",
    "모두가 공포에 빠졌을 때 파는 것이 가장 비싼 실수일 수 있다.",
    "좋은 소식만큼 나쁜 소식도 읽어야 한다.",
    "자주 바꾸는 것보다 근거 있게 바꾸는 것이 중요하다.",
]
render(
    '<div class="glass mm"><div class="label">Take-home Points</div><div class="points">'
    + "".join(f'<div class="point">{p}</div>' for p in POINTS)
    + "</div></div>"
)

spacer(4)
c = st.columns([1, 1, 1])[1]
with c:
    st.button("↺  새 게임 시작", on_click=reset_game, type="primary")
