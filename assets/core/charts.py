"""
라이브러리 없이 직접 그리는 SVG 차트.
색을 CSS 변수(var(--accent) 등)로 칠하기 때문에 monochrome 모드에 맞춰 자동으로 바뀝니다.
"""


def line_chart(series, height=200, uid="c", grid=True):
    """series: [(값 리스트, 'var(--accent)' 같은 색, 면 채우기 여부), ...]"""
    W, H = 600, height
    values = [v for vals, _, _ in series for v in vals]
    lo, hi = min(values), max(values)
    pad = (hi - lo) * 0.15 or abs(hi) * 0.05 or 1
    lo, hi = lo - pad, hi + pad
    n = max(len(vals) for vals, _, _ in series)

    def points(vals):
        if len(vals) == 1:
            vals = vals * 2
        step = W / max(len(vals) - 1, 1) if n > 1 else W
        return [(i * step, H - (v - lo) / (hi - lo) * H) for i, v in enumerate(vals)]

    parts = []
    if grid:
        for k in (0.25, 0.5, 0.75):
            y = H * k
            parts.append(
                f'<line x1="0" y1="{y:.1f}" x2="{W}" y2="{y:.1f}" '
                f'style="stroke:var(--glass-border);stroke-width:1;stroke-dasharray:4 6" '
                f'vector-effect="non-scaling-stroke"/>'
            )
    defs = []
    for idx, (vals, color, fill) in enumerate(series):
        pts = points(vals)
        line = " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)
        if fill:
            gid = f"g_{uid}_{idx}"
            defs.append(
                f'<linearGradient id="{gid}" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0%" style="stop-color:{color};stop-opacity:.32"/>'
                f'<stop offset="100%" style="stop-color:{color};stop-opacity:0"/></linearGradient>'
            )
            area = f"0,{H} " + line + f" {pts[-1][0]:.1f},{H}"
            parts.append(f'<polygon points="{area}" fill="url(#{gid})"/>')
        parts.append(
            f'<polyline points="{line}" fill="none" style="stroke:{color};stroke-width:2.6;'
            f'stroke-linejoin:round;stroke-linecap:round" vector-effect="non-scaling-stroke"/>'
        )
    return (
        f'<svg class="chart" viewBox="0 0 {W} {H}" preserveAspectRatio="none" style="height:{H}px">'
        f'<defs>{"".join(defs)}</defs>{"".join(parts)}</svg>'
    )


def sparkline(values, color, uid, height=46):
    return line_chart([(values, color, True)], height=height, uid=uid, grid=False)
