"""
게임 엔진 — 시나리오, 포트폴리오 계산, 턴 진행, 돌발 이벤트, 투자 습관(편향) 분석, 경험치 정산.

[이 파일의 구성]
  1) 상태      : 게임 한 판의 데이터(new_game)와 불러오기·초기화
  2) 돌발 이벤트 : 달마다 뜨는 선택지와 그 선택이 만드는 제한
  3) 한 달 진행 : advance() — 비중 → 거래 비용 → 시장 수익률 반영
  4) 결과 분석  : 수익률·최대 낙폭·등급, 투자 습관(행동 편향) 탐지
  5) 정산      : 게임이 끝났을 때 XP와 배지를 한 번만 지급

[예외 상황 처리 — 이 파일에서 막는 것들]
  - 저장된 시나리오 번호가 잘못된 경우       → get_game()이 새 게임으로 되돌림
  - 이벤트 제한을 어긴 비중 / 합계 100% 초과  → advance()가 보정·거부 (False 반환)
  - 비중 값이 비어 있거나 숫자가 아닌 경우     → advance()의 try/except가 거부
  - 총자산이 0이거나 기록이 비어 있는 경우    → max_drawdown()·metrics()가 0으로 안전 처리
"""
import uuid

import streamlit as st

from core.progress import add_xp, unlock, profile
from data.events import EVENTS, STOCKS, GOOD_FLAGS
from data.market import IDS, START_CASH, FEE_RATE, CASH_RATE
from data.scenarios import SCENARIOS


# ── 1) 상태 ─────────────────────────────────────────────
def new_game(sid=None):
    """게임 한 판의 초기 상태를 만든다. sid는 고른 시나리오 번호(없으면 None)."""
    return {
        "gid": uuid.uuid4().hex[:8],             # 게임마다 다른 번호 (XP 중복 지급 방지)
        "sid": sid,                              # 고른 시나리오 (None이면 아직 안 고름)
        "turn": 0,                               # 지금까지 끝난 달 수 (0~12)
        "cash": float(START_CASH),
        "hold": {a: 0.0 for a in IDS},           # 자산별 보유 금액
        "targets": {a: 0 for a in IDS},          # 직전 달에 정한 비중(%)
        "history": [],                           # 달마다의 기록
        "values": [float(START_CASH)],           # 월말 총자산 흐름
        "events": {},                            # {달: 고른 보기 번호}
        "finalized": False,
    }


def get_game():
    """지금 진행 중인 게임을 돌려준다. 없거나 데이터가 망가졌으면 새 게임으로 되돌린다. (예외 처리 ①)"""
    g = st.session_state.get("game")
    broken = (
        not isinstance(g, dict)
        or (g.get("sid") is not None and g["sid"] not in SCENARIOS)  # 존재하지 않는 시나리오
    )
    if broken:
        st.session_state.game = new_game()
    return st.session_state.game


def reset_game():
    """게임을 처음 상태로 되돌린다. (XP·배지는 유지)"""
    st.session_state.game = new_game()


def choose_scenario(sid):
    """시나리오를 골라 새 게임을 시작한다. 모르는 시나리오 번호는 무시한다."""
    if sid not in SCENARIOS:
        return
    st.session_state.game = new_game(sid)


def sc(g):
    """이 게임의 시나리오 데이터 (months / returns / prices / bench / tags ...)"""
    return SCENARIOS[g["sid"]]


def total(g):
    """현금 + 모든 자산 보유 금액 = 지금 총자산"""
    return g["cash"] + sum(g["hold"].values())


def is_over(g):
    """12개월을 모두 보냈으면 True"""
    return g["sid"] is not None and g["turn"] >= len(sc(g)["months"])


# ── 2) 돌발 이벤트 ──────────────────────────────────────
def event_for(g, m):
    """m번째 달에 뜨는 이벤트(없으면 None)"""
    return EVENTS.get(g["sid"], {}).get(m)


def event_choice(g, m):
    """이 달 이벤트에서 고른 보기(dict). 아직 안 골랐거나 이벤트가 없으면 None"""
    ev = event_for(g, m)
    i = g["events"].get(m)
    return None if ev is None or i is None else ev["options"][i]


def limits_for(g, m):
    """이번 달 이벤트 선택이 정하는 제한: (최소 비중, 최대 비중, 최소 현금%)"""
    o = event_choice(g, m)
    if o is None:
        return {}, {}, 0
    return o["min"], o["max"], o["cash_min"]


def event_flags(g):
    """이벤트에서 고른 보기들의 판단 유형을 [(달, 유형), ...]로 돌려준다. (편향 분석에 쓰임)"""
    out = []
    for m, i in g["events"].items():
        f = EVENTS[g["sid"]][m]["options"][i]["flag"]
        if f:
            out.append((m, f))
    return sorted(out)


def answer_event(m, i):
    """이벤트 보기를 고른다. 이벤트가 없거나 이미 답했거나 보기 번호가 범위 밖이면 무시한다. (예외 처리 ②)"""
    g = get_game()
    ev = event_for(g, m)
    if ev is None or m in g["events"] or not (0 <= i < len(ev["options"])):
        return
    g["events"][m] = i
    flag = ev["options"][i]["flag"]
    if flag in GOOD_FLAGS:
        add_xp(10, key=f"{g['gid']}_ev{m}", reason="좋은 판단")
    if sum(1 for _, f in event_flags(g) if f == "calm") >= 2:
        unlock("skeptic")


# ── 3) 한 달 진행 ───────────────────────────────────────
def advance(targets):
    """이번 달 비중(targets, %)대로 재조정 → 거래 비용 → 한 달 시장 움직임 반영.
    정상적으로 한 달이 진행되면 True, 입력이 잘못되어 거부하면 False를 돌려준다. (예외 처리 ③)"""
    g = get_game()
    if g["sid"] is None or is_over(g):
        return False                       # 시나리오를 안 골랐거나 이미 끝난 게임
    S = sc(g)
    m = g["turn"]

    # 이벤트가 정한 최소·최대 비중 안으로 값을 보정한다.
    mins, maxs, cash_min = limits_for(g, m)
    try:
        targets = {a: int(min(max(targets[a], mins.get(a, 0)), maxs.get(a, 100))) for a in IDS}
    except (KeyError, TypeError, ValueError):
        return False                       # 자산이 빠졌거나 숫자가 아닌 값
    if sum(targets.values()) > 100 - cash_min:
        return False                       # 투자 합계가 한도(100% - 최소 현금)를 넘음

    # 재조정: 목표 비중과 현재 보유의 차이(회전율)에 거래 비용률을 곱한 만큼 수수료를 낸다.
    start = total(g)
    wanted = {a: start * targets[a] / 100 for a in IDS}
    turnover = sum(abs(wanted[a] - g["hold"][a]) for a in IDS)
    fee = turnover * FEE_RATE
    after_fee = start - fee

    hold = {a: after_fee * targets[a] / 100 for a in IDS}
    cash = after_fee - sum(hold.values())

    # 이번 달 시장 수익률 반영 (현금은 월 이자)
    R = S["returns"][m]
    hold = {a: v * (1 + R[a]) for a, v in hold.items()}
    cash *= 1 + CASH_RATE
    end = cash + sum(hold.values())

    g["hold"], g["cash"] = hold, cash
    g["history"].append({"month": m, "targets": dict(targets), "fee": fee, "start": start, "end": end})
    g["values"].append(end)
    g["targets"] = dict(targets)
    g["turn"] += 1

    label = S["months"][m]["label"]
    add_xp(5, key=f"{g['gid']}_m{m}", reason=f"{label} 결정")
    unlock("first_step")
    return True


# ── 4) 결과 분석 ────────────────────────────────────────
def max_drawdown(values):
    """최대 낙폭(MDD): 고점 대비 가장 크게 떨어진 비율. 값이 비었거나 고점이 0이면 0 (예외 처리 ④)"""
    if not values:
        return 0.0
    peak, mdd = values[0], 0.0
    for v in values:
        peak = max(peak, v)
        if peak > 0:                        # 0으로 나누기 방지
            mdd = max(mdd, (peak - v) / peak)
    return mdd


def metrics(g):
    """수익률·벤치마크·최대 낙폭·수수료·등급(S/A/B/C)을 계산한다."""
    S = sc(g)
    final = g["values"][-1]
    turns = min(g["turn"], len(S["bench"]) - 1)   # 벤치마크 범위를 벗어나지 않게
    ret = final / START_CASH - 1
    bench = S["bench"][turns] / START_CASH - 1
    mdd = max_drawdown(g["values"])
    fees = sum(h["fee"] for h in g["history"])
    excess = ret - bench                     # 시장(벤치마크)을 이긴 정도
    if excess >= 0.03 and mdd <= 0.12:
        grade = "S"
    elif excess >= 0:
        grade = "A"
    elif ret >= 0:
        grade = "B"
    else:
        grade = "C"
    return {"final": final, "ret": ret, "bench": bench, "mdd": mdd, "fees": fees, "grade": grade}


def detect_biases(g):
    """기록과 이벤트 선택을 보고 투자 습관(행동 편향)을 찾아냅니다."""
    S = sc(g)
    R, tags = S["returns"], S["tags"]
    H = g["history"]
    found = []
    if not H:
        return found

    flags = event_flags(g)

    def flagged(f):
        return [m for m, x in flags if x == f and m < len(H)]

    # 1) 군중 심리 (FOMO): 크게 오른 종목을 뒤늦게 늘림 / 루머 종목 추격 / 이벤트에서 따라 삼
    fomo = []
    for t in range(1, len(H)):
        for a in STOCKS:
            if H[t]["targets"][a] - H[t - 1]["targets"][a] >= 15 and R[t - 1][a] >= 0.15:
                fomo.append(t)
    for t, tg in tags.items():
        a = tg.get("rumor")
        if a and t < len(H) and H[t]["targets"][a] >= 15:
            fomo.append(t)
    fomo += flagged("herd")
    if fomo:
        found.append({
            "kind": "warn", "name": "군중 심리", "en": "Herd Behavior · FOMO",
            "months": sorted(set(fomo)),
            "text": "이미 크게 오른 종목이나 루머가 도는 종목을 뒤늦게 많이 샀어요. '나만 뒤처질까' 하는 불안이 판단을 앞질렀어요.",
            "tip": "사기 전에 '이 가격이 오른 근거가 무엇인가?'를 한 문장으로 적어 보세요. 근거가 '다들 사니까'라면 멈춤.",
        })

    # 2) 공포 매도: 큰 하락 직후 비중을 크게 줄였는데, 바로 다음 달 반등
    panic = []
    for t in range(1, len(H)):
        for a in STOCKS:
            prev, now = H[t - 1]["targets"][a], H[t]["targets"][a]
            if prev >= 15 and now <= prev - 15 and R[t - 1][a] <= -0.08 and R[t][a] > 0:
                panic.append(t)
    panic += flagged("panic")
    if panic:
        found.append({
            "kind": "warn", "name": "공포 매도 · 손실 회피", "en": "Panic Selling · Loss Aversion",
            "months": sorted(set(panic)),
            "text": "가격이 크게 떨어진 직후 팔았고, 그 뒤 시장이 반등했어요. 손실의 고통을 피하려다 회복의 기회까지 놓쳤어요.",
            "tip": "급락한 달에는 '회사(자산)의 가치가 바뀌었나, 가격만 바뀌었나?'를 먼저 구분해 보세요.",
        })

    # 3) 과잉 확신: 한 자산에 50% 이상 몰빵 / 이벤트에서 욕심을 택함
    conc = [t for t in range(len(H)) if any(H[t]["targets"][a] >= 50 for a in IDS if a != "bond")]
    conc += flagged("greed")
    if conc:
        found.append({
            "kind": "warn", "name": "과잉 확신 · 몰빵", "en": "Overconfidence · Concentration",
            "months": sorted(set(conc)),
            "text": "한 자산에 아주 큰 비중을 걸었어요. 예측이 맞으면 크게 벌지만, 틀리면 회복하기 어려운 손실이 나요.",
            "tip": "한 자산의 비중 상한선(예: 30%)을 미리 정해 두는 것이 가장 간단한 안전장치예요.",
        })

    # 4) 확증 편향: 경고가 숨어 있던 달에 그 자산을 크게 보유 / 이벤트에서 좋은 말만 믿음
    conf = []
    for t, tg in tags.items():
        a = tg.get("warning")
        if a and t < len(H) and H[t]["targets"][a] >= 30:
            conf.append(t)
    conf += flagged("confirm")
    if conf:
        found.append({
            "kind": "warn", "name": "확증 편향", "en": "Confirmation Bias",
            "months": sorted(set(conf)),
            "text": "신고가 같은 좋은 소식에 집중하고, 같은 기사 속에 있던 경고는 가볍게 넘겼어요.",
            "tip": "보유 종목에 대해 '반대 의견'을 일부러 하나 찾아 읽는 습관을 들여 보세요.",
        })

    # 5) 과잉 매매: 매달 포트폴리오를 크게 갈아엎음
    if len(H) >= 3:
        changes = [sum(abs(H[t]["targets"][a] - H[t - 1]["targets"][a]) for a in IDS) / 2 for t in range(1, len(H))]
        avg_change = sum(changes) / len(changes)
        if avg_change >= 35:
            found.append({
                "kind": "warn", "name": "과잉 매매", "en": "Overtrading",
                "months": [],
                "text": f"매달 평균 {avg_change:.0f}%씩 포트폴리오를 바꿨어요. 거래 비용이 쌓이고, 결정이 잦을수록 실수할 기회도 늘어나요.",
                "tip": "바꾸기 전에 '지난달과 무엇이 달라졌나?'를 확인하세요. 달라진 게 없다면 그대로 두는 것도 결정이에요.",
            })

    # 6) 현금 과다: 평균 절반 이상을 현금으로
    avg_cash = sum(100 - sum(h["targets"].values()) for h in H) / len(H)
    if avg_cash >= 50:
        found.append({
            "kind": "warn", "name": "지나친 위험 회피", "en": "Excessive Risk Aversion",
            "months": [],
            "text": f"평균 {avg_cash:.0f}%를 현금으로 들고 있었어요. 잃지는 않았지만, 시장이 주는 기회도 대부분 지나쳤어요.",
            "tip": "채권·금처럼 변동성이 낮은 자산으로 '덜 위험하게 투자하는 방법'도 있어요.",
        })

    # ── 잘한 점 ──
    held = [sum(1 for a in IDS if h["targets"][a] > 0) for h in H]
    max_w = max(max(h["targets"].values()) for h in H)
    if sum(held) / len(held) >= 4 and max_w < 40:
        found.append({
            "kind": "good", "name": "분산 투자", "en": "Diversification",
            "months": [],
            "text": "평균 4개 이상의 자산에 고르게 나눠 담았어요. 급락기에도 충격이 작았을 거예요.",
            "tip": "이 습관을 그대로 유지하세요. 서로 다르게 움직이는 자산을 섞는 것이 핵심이에요.",
        })

    patient = []
    for t, tg in tags.items():
        if tg.get("panic") and t + 1 < len(H):
            s0 = sum(H[t]["targets"][a] for a in STOCKS)
            s1 = sum(H[t + 1]["targets"][a] for a in STOCKS)
            if s0 >= 30 and s1 >= s0:
                patient.append(t + 1)
    if not patient and "panic" not in [f for _, f in flags]:
        # 이벤트에서 '버티기'를 골랐고, 그 달에 실제로 주식을 30% 이상 들고 있었던 경우
        patient = [m for m, f in flags if f == "patient" and m < len(H) and sum(H[m]["targets"][a] for a in STOCKS) >= 30]
    if patient:
        found.append({
            "kind": "good", "name": "공포 속의 인내", "en": "Staying the Course",
            "months": sorted(set(patient)),
            "text": "모두가 불안해하던 시기에도 주식 비중을 유지했어요. 그 덕분에 이어진 반등을 온전히 누렸어요.",
            "tip": "시장의 분위기와 자산의 가치를 구분하는 힘, 장기 투자자의 가장 중요한 무기예요.",
        })
    return found


# ── 5) 게임이 끝났을 때 한 번만: 경험치·배지 정산 ────────────
def finalize(g):
    """12개월이 끝났을 때 딱 한 번 XP와 배지를 지급한다. (finalized 표시로 중복 지급 방지)"""
    if g.get("finalized") or not is_over(g):
        return
    g["finalized"] = True
    k = metrics(g)
    biases = detect_biases(g)

    add_xp(30, key=f"{g['gid']}_done", reason="12개월 완주")
    unlock("survivor")
    add_xp({"S": 50, "A": 30, "B": 15, "C": 5}[k["grade"]], key=f"{g['gid']}_grade", reason=f"투자자 등급 {k['grade']}")
    if k["grade"] == "S":
        unlock("s_grade")

    names = {b["name"] for b in biases}
    if "분산 투자" in names:
        unlock("diversifier")
    if "공포 속의 인내" in names:
        unlock("patient")
    if not any(b["kind"] == "warn" for b in biases):
        unlock("clean")

    p = profile()
    if g["sid"] not in p["scenarios_done"]:
        p["scenarios_done"].append(g["sid"])
    if len(p["scenarios_done"]) >= 2:
        unlock("explorer")
    if len(p["scenarios_done"]) >= len(SCENARIOS):
        unlock("conqueror")
