"""
가상 시장 데이터 — 기업 7개 + 12개월 시나리오.
※ 모든 기업·뉴스·숫자는 교육용으로 만든 가상의 데이터입니다.

월별 수익률(base)을 바꾸면 게임 난이도와 이야기가 바뀝니다.
0.10 = +10%, -0.45 = -45%
"""
import random

START_CASH = 10_000_000   # 시작 자금 1,000만 원
FEE_RATE = 0.002          # 거래 비용 0.2% (사고판 금액 기준)
CASH_RATE = 0.0025        # 현금 이자 월 0.25%

ASSETS = [
    {"id": "nova", "name": "노바 반도체", "ticker": "NOVA", "sector": "Tech", "risk": "High", "price": 52000,
     "color": "var(--accent)", "desc": "AI 서버용 칩을 만드는 성장주. 기대가 크고 변동성도 크다."},
    {"id": "halo", "name": "헤일로 바이오", "ticker": "HALO", "sector": "Bio", "risk": "Very High", "price": 38000,
     "color": "#FF8FB1", "desc": "신약 하나에 회사의 운명이 걸린 바이오 기업."},
    {"id": "green", "name": "그린라인 에너지", "ticker": "GRNL", "sector": "Energy", "risk": "Mid", "price": 27000,
     "color": "#7BD88F", "desc": "태양광·풍력 발전 기업. 정부 정책의 영향을 크게 받는다."},
    {"id": "mart", "name": "어반마트", "ticker": "URBN", "sector": "Consumer", "risk": "Low", "price": 64000,
     "color": "#F2C66D", "desc": "생필품 유통 기업. 경기가 나빠도 매출이 크게 줄지 않는다."},
    {"id": "bank", "name": "아스터 은행", "ticker": "ASTR", "sector": "Finance", "risk": "Mid", "price": 41000,
     "color": "#75C3D1", "desc": "금리가 오르면 이익이 늘어나는 경향이 있는 은행주."},
    {"id": "bond", "name": "국채 ETF", "ticker": "BOND", "sector": "Bond", "risk": "Low", "price": 10000,
     "color": "var(--neon)", "desc": "나라가 발행한 채권에 투자. 금리가 오르면 가격이 내려간다."},
    {"id": "gold", "name": "금 ETF", "ticker": "GOLD", "sector": "Commodity", "risk": "Mid", "price": 15000,
     "color": "#C9A66B", "desc": "불안할 때 사람들이 찾는 안전자산. 주식과 반대로 움직일 때가 많다."},
]
ASSET_MAP = {a["id"]: a for a in ASSETS}
IDS = [a["id"] for a in ASSETS]

# 각 달: 결정 '전'에 보이는 뉴스/지표 + 그 달의 실제 시장 움직임(base) + 디브리핑용 해설(after)
MONTHS = [
    {"label": "January", "headline": "새해 첫 달, 중앙은행 기준금리 동결",
     "body": "시장은 잔잔하게 출발했다. 전문가들은 '올해는 변동성이 클 것'이라고만 말한다.",
     "rate": 3.00, "cpi": 2.4, "mood": 55,
     "base": {"nova": .02, "halo": .01, "green": .01, "mart": .01, "bank": .01, "bond": .003, "gold": .0},
     "after": "조용한 출발. 이 달의 선택은 '나의 기본 성향'을 보여준다."},
    {"label": "February", "headline": "빅테크들, AI 서버 투자 확대 잇따라 발표",
     "body": "대형 IT 기업들이 데이터센터 투자를 늘리겠다고 밝혔다. 반도체 업계가 들썩인다.",
     "rate": 3.00, "cpi": 2.5, "mood": 66,
     "base": {"nova": .18, "halo": .03, "green": .02, "mart": .01, "bank": .02, "bond": .0, "gold": -.01},
     "after": "노바 반도체 +18%. 실제 수요 증가라는 '근거'가 있는 상승이었다."},
    {"label": "March", "headline": "\"헤일로 신약, 대박 난다\" SNS에서 루머 확산",
     "body": "커뮤니티에 '임상 성공 확정'이라는 글이 퍼지며 개인 투자자들이 몰리고 있다. 회사는 공식 입장을 내지 않았다.",
     "rate": 3.00, "cpi": 2.7, "mood": 78,
     "base": {"nova": .04, "halo": .25, "green": .01, "mart": .0, "bank": .01, "bond": .0, "gold": -.01},
     "after": "헤일로 +25%. 근거 없는 루머만으로 가격이 올랐다. 투자 심리 지수는 '탐욕' 구간."},
    {"label": "April", "headline": "헤일로 바이오, 임상 3상 결과 발표 임박",
     "body": "결과 발표를 앞두고 거래량이 사상 최대다. '지금이라도 타야 한다'는 글이 쏟아진다.",
     "rate": 3.00, "cpi": 2.9, "mood": 72,
     "base": {"nova": .02, "halo": -.45, "green": .0, "mart": .01, "bank": .0, "bond": .005, "gold": .01},
     "after": "임상 실패 발표. 헤일로 -45%. 루머를 믿고 늦게 들어간 투자자가 가장 크게 다쳤다."},
    {"label": "May", "headline": "물가 3개월 연속 상승… 금리 인상 가능성 커져",
     "body": "소비자물가가 목표치를 넘어섰다. 시장은 중앙은행의 다음 행보에 주목하고 있다.",
     "rate": 3.00, "cpi": 3.4, "mood": 48,
     "base": {"nova": -.08, "halo": -.05, "green": -.06, "mart": -.01, "bank": .06, "bond": -.04, "gold": .03},
     "after": "금리 인상 우려에 성장주와 채권이 하락, 은행과 금은 상승했다."},
    {"label": "June", "headline": "중앙은행, 기준금리 0.5%p 전격 인상",
     "body": "예상보다 큰 인상 폭에 시장이 충격을 받았다. 공포 지수가 1년 만에 최고치를 기록했다.",
     "rate": 3.50, "cpi": 3.6, "mood": 18,
     "base": {"nova": -.12, "halo": -.10, "green": -.09, "mart": -.03, "bank": -.04, "bond": -.02, "gold": .05},
     "after": "전 종목 하락, 금만 올랐다. 이때 분산투자를 했다면 손실이 훨씬 작았다."},
    {"label": "July", "headline": "\"아직 바닥 아니다\" 전문가들 추가 하락 경고",
     "body": "투자자들이 시장을 떠나고 있다. 뉴스마다 '더 떨어진다'는 전망이 넘친다.",
     "rate": 3.50, "cpi": 3.3, "mood": 22,
     "base": {"nova": .12, "halo": .08, "green": .09, "mart": .03, "bank": .07, "bond": .01, "gold": -.02},
     "after": "모두가 비관할 때 시장은 반등했다. 공포에 판 투자자는 반등을 놓쳤다."},
    {"label": "August", "headline": "친환경 에너지 보조금 법안, 국회 본회의 상정",
     "body": "통과되면 재생에너지 기업들이 큰 혜택을 받는다. 통과 가능성은 높게 점쳐진다.",
     "rate": 3.50, "cpi": 3.0, "mood": 50,
     "base": {"nova": .03, "halo": .02, "green": .20, "mart": .01, "bank": .02, "bond": .0, "gold": .0},
     "after": "법안 통과. 그린라인 +20%. 정책이라는 구체적 근거가 있는 변화였다."},
    {"label": "September", "headline": "소비 심리 위축, 경기 둔화 신호 뚜렷",
     "body": "카드 사용액이 줄고 기업들이 채용을 늦추고 있다. 그래도 생필품 소비는 꾸준하다.",
     "rate": 3.50, "cpi": 2.8, "mood": 40,
     "base": {"nova": -.05, "halo": -.04, "green": -.03, "mart": .02, "bank": -.04, "bond": .02, "gold": .02},
     "after": "경기 둔화기에는 생필품주·채권·금 같은 '방어 자산'이 버텼다."},
    {"label": "October", "headline": "중앙은행 총재 \"금리 인하 검토할 시점\"",
     "body": "물가가 안정되자 중앙은행이 금리 인하 가능성을 처음으로 언급했다.",
     "rate": 3.50, "cpi": 2.5, "mood": 58,
     "base": {"nova": .10, "halo": .05, "green": .06, "mart": .02, "bank": -.03, "bond": .05, "gold": .01},
     "after": "금리 인하 기대에 채권과 성장주가 올랐고, 은행은 약해졌다."},
    {"label": "November", "headline": "노바 반도체 주가 사상 최고… 한편 '반도체 재고 증가' 보도",
     "body": "주가는 연일 신고가지만, 일부 언론은 업계에 재고가 쌓이고 있다고 지적한다. 투자 심리는 '극단적 탐욕'.",
     "rate": 3.25, "cpi": 2.4, "mood": 82,
     "base": {"nova": -.15, "halo": .02, "green": .02, "mart": .01, "bank": .01, "bond": .01, "gold": .0},
     "after": "공급 과잉이 확인되며 노바 -15%. 좋은 소식만 골라 믿는 확증 편향이 위험했던 달."},
    {"label": "December", "headline": "연말 '산타 랠리' 기대감",
     "body": "한 해를 마무리하며 시장 분위기가 다시 밝아지고 있다.",
     "rate": 3.25, "cpi": 2.3, "mood": 68,
     "base": {"nova": .05, "halo": .04, "green": .05, "mart": .02, "bank": .04, "bond": .005, "gold": -.01},
     "after": "대부분 자산이 소폭 상승하며 한 해가 끝났다."},
]

# 실제 수익률 = base + 작은 랜덤 흔들림 (seed 고정 → 누구나 같은 시장을 경험)
_rng = random.Random(2027)
RETURNS = []
for _m in MONTHS:
    month = {}
    for _a in IDS:
        noise = _rng.uniform(-0.015, 0.015) * (0.3 if _a == "bond" else 1)
        month[_a] = round(_m["base"][_a] + noise, 4)
    RETURNS.append(month)

# 가격 흐름 (0번 = 시작 가격, 12번 = 12월 말 가격)
PRICES = {}
for _a in ASSETS:
    p = [_a["price"]]
    for _r in RETURNS:
        p.append(p[-1] * (1 + _r[_a["id"]]))
    PRICES[_a["id"]] = p

# 비교 기준(벤치마크): 7개 자산에 똑같이 나눠 1년간 그대로 둔 경우
BENCH = [START_CASH]
for _t in range(1, len(MONTHS) + 1):
    BENCH.append(sum(START_CASH / len(IDS) * PRICES[a][_t] / PRICES[a][0] for a in IDS))
