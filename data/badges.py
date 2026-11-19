"""
레벨과 배지 정의.
XP는 Academy 퀴즈, 매달의 결정, 예측, 좋은 판단, 게임 완주로 쌓입니다.
"""
# (이 레벨이 되기 위한 누적 XP, 칭호)
LEVELS = [
    (0, "새싹 투자자"),
    (100, "관찰자"),
    (250, "분석가"),
    (450, "전략가"),
    (700, "마스터"),
]
BADGES = [
    {"id": "quiz_pass", "name": "개념 학습", "desc": "Academy 퀴즈를 통과했어요", "glyph": "◆"},
    {"id": "perfect", "name": "만점 학습자", "desc": "Academy 퀴즈를 모두 맞혔어요", "glyph": "★"},
    {"id": "first_step", "name": "첫 걸음", "desc": "첫 달의 결정을 확정했어요", "glyph": "●"},
    {"id": "skeptic", "name": "의심하는 투자자", "desc": "한 게임에서 '근거 확인' 선택을 2번 했어요", "glyph": "?"},
    {"id": "survivor", "name": "완주", "desc": "12개월을 끝까지 마쳤어요", "glyph": "✓"},
    {"id": "diversifier", "name": "분산의 정석", "desc": "'분산 투자' 강점을 얻었어요", "glyph": "▦"},
    {"id": "patient", "name": "공포 속 인내", "desc": "'공포 속의 인내' 강점을 얻었어요", "glyph": "◐"},
    {"id": "oracle", "name": "촉이 좋은 사람", "desc": "한 게임에서 예측을 8번 이상 맞혔어요", "glyph": "✦"},
    {"id": "s_grade", "name": "시장을 이긴 자", "desc": "투자자 등급 S를 받았어요", "glyph": "S"},
    {"id": "clean", "name": "습관 청정", "desc": "주의할 투자 습관이 하나도 없었어요", "glyph": "◎"},
    {"id": "explorer", "name": "시나리오 탐험가", "desc": "서로 다른 시장 2가지를 완주했어요", "glyph": "▲"},
    {"id": "conqueror", "name": "3대 시장 정복", "desc": "모든 시장(시나리오)을 완주했어요", "glyph": "♛"},
]
BADGE_MAP = {b["id"]: b for b in BADGES}
