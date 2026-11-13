"""Glossary — 투자 용어 사전"""
from html import escape

import streamlit as st

from core.ui import render, section_head
from data.glossary import GLOSSARY

render('<div class="page-head"></div>')
section_head(
    "Glossary",
    "시장을 읽는 단어들",
    "게임을 하다 막히는 용어가 있다면 여기서 찾아보세요. 경제를 처음 공부하는 학생도 이해할 수 있게 풀어 썼습니다.",
)

query = st.text_input("검색", placeholder="용어를 검색해 보세요 — 예: 금리, 편향, ETF", label_visibility="collapsed")
q = query.strip().lower()
items = [g for g in GLOSSARY if not q or any(q in s.lower() for s in g)]

if not items:
    render('<div class="glass mm" style="margin-top:20px">검색 결과가 없어요. 다른 단어로 찾아볼까요?</div>')
else:
    render(
        '<div class="grid mm" style="margin-top:22px">'
        + "".join(
            f'<div class="glass lift term"><div class="t">{escape(t)}</div>'
            f'<div class="en">{escape(en)}</div><div class="d">{escape(d)}</div></div>'
            for t, en, d in items
        )
        + "</div>"
    )
