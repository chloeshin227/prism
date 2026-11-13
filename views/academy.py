"""Academy — 레슨 카드 학습 → 확인 퀴즈 → 통과하면 Trading Floor 잠금 해제"""
from html import escape

import streamlit as st

from core.ui import render, section_head, spacer
from data.lessons import LESSONS, QUIZ, PASS_SCORE

ss = st.session_state
ss.setdefault("quiz_answers", None)   # 채점 후 {문제번호: 고른 보기}
ss.setdefault("unlocked", False)

LETTERS = "ABCD"


def grade_quiz():
    ss.quiz_answers = {i: ss.get(f"quiz_{i}") for i in range(len(QUIZ))}
    score = sum(ss.quiz_answers[i] == q["answer"] for i, q in enumerate(QUIZ))
    if score >= PASS_SCORE:
        ss.unlocked = True


def retry_quiz():
    ss.quiz_answers = None
    for i in range(len(QUIZ)):
        ss.pop(f"quiz_{i}", None)


# ── 1. 레슨 ─────────────────────────────────────────────
render('<div class="page-head"></div>')
section_head(
    "Academy",
    "시장에 들어가기 전,<br>다섯 장의 카드.",
    "실제 게임에서 바로 쓰이는 개념만 골랐어요. 한 장에 1분이면 충분합니다.",
)
render(
    '<div class="grid mm">'
    + "".join(
        f'<div class="glass lift lesson reveal"><div class="no">{l["no"]}</div>'
        f'<div class="t">{l["title"]}</div><div class="en">{l["en"]}</div>'
        f'<div class="d">{escape(l["body"])}</div><div class="key">{escape(l["key"])}</div></div>'
        for l in LESSONS
    )
    + "</div>"
)

spacer(12)

# ── 2. 퀴즈 ─────────────────────────────────────────────
section_head(
    "Checkpoint",
    "이해했는지 확인해 볼까요?",
    f"{len(QUIZ)}문제 중 {PASS_SCORE}문제 이상 맞히면 Trading Floor가 열립니다.",
)

if ss.quiz_answers is None:
    for i, q in enumerate(QUIZ):
        render(
            f"""
            <div class="glass q-card mm" style="margin:14px 0 12px">
              <div class="q-no">Q{i + 1}</div>
              <div class="q-text">{escape(q['q'])}</div>
            </div>
            """
        )
        st.radio(
            f"Q{i + 1}",
            options=list(range(len(q["options"]))),
            format_func=lambda k, q=q: f"{LETTERS[k]}.   {q['options'][k]}",
            index=None,
            key=f"quiz_{i}",
            label_visibility="collapsed",
        )
    spacer(2)
    all_done = all(ss.get(f"quiz_{i}") is not None for i in range(len(QUIZ)))
    with st.container(key="grade"):
        st.button("채점하기  →", type="primary", disabled=not all_done, on_click=grade_quiz)
else:
    score = sum(ss.quiz_answers[i] == q["answer"] for i, q in enumerate(QUIZ))
    passed = score >= PASS_SCORE
    msg = "Trading Floor가 열렸어요. 이제 진짜 시장으로!" if passed else "조금만 더! 카드를 다시 읽고 재도전해 보세요."
    render(
        f"""
        <div class="mm" style="display:flex;gap:28px;align-items:center;flex-wrap:wrap;margin-bottom:24px">
          <div class="score-box"><b>{score}/{len(QUIZ)}</b><span>{"Passed" if passed else "Try again"}</span></div>
          <div class="section-sub" style="font-weight:700">{msg}</div>
        </div>
        """
    )
    for i, q in enumerate(QUIZ):
        chosen, a = ss.quiz_answers[i], q["answer"]
        ok = chosen == a
        verdict = '<span class="verdict ok">Correct</span>' if ok else '<span class="verdict bad">Missed</span>'
        render(
            f"""
            <div class="glass answered mm">
              <div class="ans-head"><span class="q-mini">Q{i + 1}</span>{verdict}</div>
              <div class="q-text">{escape(q['q'])}</div>
              <div class="ans-row"><span class="lbl">Your pick</span>{LETTERS[chosen]}. {escape(q['options'][chosen])}</div>
              <div class="ans-row"><span class="lbl">Answer</span>{LETTERS[a]}. {escape(q['options'][a])}</div>
              <div class="explain">{escape(q['explain'])}</div>
            </div>
            """
        )
    spacer(3)
    if passed:
        with st.container(key="end_cta"):
            st.page_link("views/trade.py", label="Trading Floor 입장하기  →")
    else:
        st.button("↺  다시 풀기", on_click=retry_quiz)
