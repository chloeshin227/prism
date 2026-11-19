"""
성장 시스템 — XP, 레벨, 배지.
브라우저를 새로고침하면 초기화되는 '세션' 기록입니다. (데이터베이스 없음)
"""
import streamlit as st
from data.badges import LEVELS, BADGES, BADGE_MAP
def profile():
    ss = st.session_state
    if "profile" not in ss:
        ss.profile = {"xp": 0, "badges": [], "awarded": [], "scenarios_done": []}
    return ss.profile
def level_of(xp: int) -> int:
    lv = 0
    for i, (need, _) in enumerate(LEVELS):
        if xp >= need:
            lv = i
    return lv
def level_info(xp=None):
    """(레벨 번호(1~), 칭호, 이번 레벨 진행 xp, 이번 레벨 필요 xp, 진행률 0~100)"""
    xp = profile()["xp"] if xp is None else xp
    lv = level_of(xp)
    cur_need, name = LEVELS[lv]
    if lv + 1 < len(LEVELS):
        nxt = LEVELS[lv + 1][0]
        span = nxt - cur_need
        done = xp - cur_need
        return lv + 1, name, done, span, min(100, done / span * 100)
    return lv + 1, name, xp - cur_need, 0, 100
def add_xp(n: int, key: str = "", reason: str = "") -> int:
    """XP를 올립니다. key가 있으면 같은 key로는 한 번만 올라요."""
    p = profile()
    if key:
        if key in p["awarded"]:
            return 0
        p["awarded"].append(key)
    before = level_of(p["xp"])
    p["xp"] += n
    st.toast(f"+{n} XP  ·  {reason}" if reason else f"+{n} XP")
    after = level_of(p["xp"])
    if after > before:
        st.toast(f"레벨 업! Lv.{after + 1} {LEVELS[after][1]}")
    return n
def unlock(badge_id: str) -> bool:
    p = profile()
    if badge_id in p["badges"] or badge_id not in BADGE_MAP:
        return False
    p["badges"].append(badge_id)
    st.toast(f"배지 획득  ·  {BADGE_MAP[badge_id]['name']}")
    return True
def xp_strip_html() -> str:
    p = profile()
    lv, name, done, span, pct = level_info()
    right = f"{done} / {span} XP" if span else "MAX"
    return (
        '<div class="xp-strip mm">'
        f'<span class="xp-lv">Lv.{lv}</span><span class="xp-name">{name}</span>'
        f'<span class="xp-bar"><i style="width:{pct:.0f}%"></i></span>'
        f'<span class="xp-num">{right}</span>'
        f'<span class="xp-badges">배지 {len(p["badges"])}/{len(BADGES)}</span>'
        "</div>"
    )
