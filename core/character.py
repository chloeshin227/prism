"""
투자 성향 캐릭터 — 한 게임의 기록과 습관 분석으로 6가지 캐릭터 중 하나를 정합니다.
"""
from data.events import STOCKS
from data.market import IDS
CHARACTERS = {
    "moth": {"glyph": "✦", "name": "불을 쫓는 불나방", "en": "The Chasing Moth",
             "line": "반짝이는 것에 가장 먼저 날아가는 투자자",
             "advice": "남들이 사는 이유가 '근거'인지 '분위기'인지 한 번만 더 물어보세요. 그 한 번이 가장 큰 방어예요."},
    "squirrel": {"glyph": "◐", "name": "겁 많은 다람쥐", "en": "The Skittish Squirrel",
                 "line": "흔들릴 때마다 도토리를 땅에 묻어 버리는 투자자",
                 "advice": "가격이 떨어졌다고 가치가 변한 건 아니에요. 팔기 전에 '지금 팔아야 할 이유'를 적어 보세요."},
    "wolf": {"glyph": "▲", "name": "외로운 늑대", "en": "The Lone Wolf",
             "line": "확신이 생기면 혼자서도 크게 걸어 버리는 투자자",
             "advice": "확신이 클수록 한 종목의 상한선이 필요해요. 틀려도 다음 판에 설 수 있도록요."},
    "bee": {"glyph": "◆", "name": "바쁜 벌", "en": "The Busy Bee",
            "line": "매달 포트폴리오를 갈아엎는 투자자",
            "advice": "바꾸기 전에 지난달과 무엇이 달라졌는지 확인하세요. 가만히 두는 것도 훌륭한 결정이에요."},
    "rock": {"glyph": "●", "name": "단단한 바위", "en": "The Steady Rock",
             "line": "시장이 흔들려도 제자리를 지키는 투자자",
             "advice": "인내는 큰 무기예요. 다만 근거가 사라졌을 때는 바꿀 줄도 알아야 해요."},
    "compass": {"glyph": "◎", "name": "균형 잡는 나침반", "en": "The Balanced Compass",
                "line": "한쪽에 치우치지 않고 방향을 잡는 투자자",
                "advice": "지금의 균형을 유지하세요. 다음엔 더 어려운 시장에서도 같은 원칙이 통하는지 시험해 보세요."},
}
# 주의 습관 → 캐릭터 (위에 있을수록 우선)
PRIORITY = [("군중 심리", "moth"), ("공포 매도 · 손실 회피", "squirrel"), ("과잉 확신 · 몰빵", "wolf"),
            ("과잉 매매", "bee"), ("지나친 위험 회피", "squirrel"), ("확증 편향", "wolf")]
def meters(g):
    """공격성 / 인내심 / 분산도 (0~100)"""
    H = g["history"]
    aggr = sum(sum(h["targets"][a] for a in STOCKS) for h in H) / len(H)
    if len(H) >= 2:
        ch = [sum(abs(H[t]["targets"][a] - H[t - 1]["targets"][a]) for a in IDS) / 2 for t in range(1, len(H))]
        patience = 100 - sum(ch) / len(ch)
    else:
        patience = 100
    held = sum(sum(1 for a in IDS if h["targets"][a] > 0) for h in H) / len(H)
    return {
        "공격성": max(0, min(100, round(aggr))),
        "인내심": max(0, min(100, round(patience))),
        "분산도": max(0, min(100, round(held / 5 * 100))),
    }
def pick(g, biases):
    names = {b["name"] for b in biases if b["kind"] == "warn"}
    for bias_name, key in PRIORITY:
        if bias_name in names:
            return CHARACTERS[key], key
    good = {b["name"] for b in biases if b["kind"] == "good"}
    if "공포 속의 인내" in good:
        return CHARACTERS["rock"], "rock"
    return CHARACTERS["compass"], "compass"
