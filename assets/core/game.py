import streamlit as st

from data.market import IDS, MONTHS, RETURNS, BENCH, START_CASH, FEE_RATE, CASH_RATE

STOCKS = ["nova", "halo", "green", "mart", "bank"]


# ── 상태 ────────────────────────────────────────────────
def new_game():
    return {
        "turn": 0,                               # 지금까지 끝난 달 수 (0~12)
        "cash": float(START_CASH),
        "hold": {a: 0.0 for a in IDS},           # 자산별 보유 금액
        "targets": {a: 0 for a in IDS},          # 직전 달에 정한 비중(%)
        "history": [],                           # 달마다의 기록
        "values": [float(START_CASH)],           # 월말 총자산 흐름
    }


def get_game():
    if "game" not in st.session_state:
        st.session_state.game = new_game()
    return st.session_state.game


def reset_game():
    st.session_state.game = new_game()


def total(g):
    return g["cash"] + sum(g["hold"].values())


def is_over(g):
    return g["turn"] >= len(MONTHS)


# ── 한 달 진행 ──────────────────────────────────────────
def advance(targets):
    """이번 달 비중(targets, %)대로 재조정 → 거래 비용 → 한 달 시장 움직임 반영"""
    g = get_game()
    if is_over(g) or sum(targets.values()) > 100:
        return
    m = g["turn"]
    start = total(g)

    wanted = {a: start * targets[a] / 100 for a in IDS}
    turnover = sum(abs(wanted[a] - g["hold"][a]) for a in IDS)
    fee = turnover * FEE_RATE
    after_fee = start - fee

    hold = {a: after_fee * targets[a] / 100 for a in IDS}
    cash = after_fee - sum(hold.values())

    hold = {a: v * (1 + RETURNS[m][a]) for a, v in hold.items()}
    cash *= 1 + CASH_RATE
    end = cash + sum(hold.values())

    g["hold"], g["cash"] = hold, cash
    g["history"].append({"month": m, "targets": dict(targets), "fee": fee, "start": start, "end": end})
    g["values"].append(end)
    g["targets"] = dict(targets)
    g["turn"] += 1


# ── 결과 분석 ───────────────────────────────────────────
def max_drawdown(values):
    peak, mdd = values[0], 0.0
    for v in values:
        peak = max(peak, v)
        mdd = max(mdd, (peak - v) / peak)
    return mdd


def metrics(g):
    final = g["values"][-1]
    turns = g["turn"]
    ret = final / START_CASH - 1
    bench = BENCH[turns] / START_CASH - 1
    mdd = max_drawdown(g["values"])
    fees = sum(h["fee"] for h in g["history"])
    excess = ret - bench
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
    """기록을 보고 투자 습관(행동 편향)을 찾아냅니다."""
    H = g["history"]
    found = []
    if not H:
        return found

    # 1) 군중 심리 (FOMO): 직전 달 크게 오른 종목을 뒤늦게 크게 늘림 + 루머 종목 추격
    fomo = []
    for t in range(1, len(H)):
        for a in STOCKS:
            if H[t]["targets"][a] - H[t - 1]["targets"][a] >= 15 and RETURNS[t - 1][a] >= 0.15:
                fomo.append(t)
    if len(H) > 3 and H[3]["targets"]["halo"] >= 15:
        fomo.append(3)
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
            if prev >= 15 and now <= prev - 15 and RETURNS[t - 1][a] <= -0.08 and RETURNS[t][a] > 0:
                panic.append(t)
    if panic:
        found.append({
            "kind": "warn", "name": "공포 매도 · 손실 회피", "en": "Panic Selling · Loss Aversion",
            "months": sorted(set(panic)),
            "text": "가격이 크게 떨어진 직후 팔았고, 그 뒤 시장이 반등했어요. 손실의 고통을 피하려다 회복의 기회까지 놓쳤어요.",
            "tip": "급락한 달에는 '회사(자산)의 가치가 바뀌었나, 가격만 바뀌었나?'를 먼저 구분해 보세요.",
        })

    # 3) 과잉 확신: 한 자산에 50% 이상 몰빵
    conc = [t for t in range(len(H)) if any(H[t]["targets"][a] >= 50 for a in IDS if a != "bond")]
    if conc:
        found.append({
            "kind": "warn", "name": "과잉 확신 · 몰빵", "en": "Overconfidence · Concentration",
            "months": conc,
            "text": "한 자산에 절반 이상을 걸었어요. 예측이 맞으면 크게 벌지만, 틀리면 회복하기 어려운 손실이 나요.",
            "tip": "한 자산의 비중 상한선(예: 30%)을 미리 정해 두는 것이 가장 간단한 안전장치예요.",
        })

    # 4) 확증 편향: '재고 증가' 경고가 있던 11월에도 노바를 크게 보유
    if len(H) > 10 and H[10]["targets"]["nova"] >= 30:
        found.append({
            "kind": "warn", "name": "확증 편향", "en": "Confirmation Bias",
            "months": [10],
            "text": "주가 신고가라는 좋은 소식에 집중하고, 같은 기사에 있던 '재고 증가' 경고는 가볍게 넘겼어요.",
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
            "text": "평균 4개 이상의 자산에 고르게 나눠 담았어요. 6월 같은 급락기에도 충격이 작았을 거예요.",
            "tip": "이 습관을 그대로 유지하세요. 서로 다르게 움직이는 자산을 섞는 것이 핵심이에요.",
        })
    if len(H) > 6:
        stock_june = sum(H[5]["targets"][a] for a in STOCKS)
        stock_july = sum(H[6]["targets"][a] for a in STOCKS)
        if stock_june >= 30 and stock_july >= stock_june:
            found.append({
                "kind": "good", "name": "공포 속의 인내", "en": "Staying the Course",
                "months": [6],
                "text": "모두가 '더 떨어진다'고 말하던 7월에도 주식 비중을 유지했어요. 그 덕분에 반등을 온전히 누렸어요.",
                "tip": "시장의 분위기와 자산의 가치를 구분하는 힘, 장기 투자자의 가장 중요한 무기예요.",
            })
    return found
