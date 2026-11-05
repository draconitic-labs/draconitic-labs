#!/usr/bin/env python3
"""The Draconitic dragon, redrawn as clean vector geometry in the coordinates of the old mark.

Writes the master SVG on black and with a transparent ground. Run with a version label.
"""
import math, pathlib, sys

OUT = pathlib.Path(__file__).parent
HOT, RED, DEEP = "#ff3d66", "#ff1745", "#c70f39"
MEMBRANE_NEAR, MEMBRANE_FAR = "#a50c30", "#7e0a26"


def cubic(p0, p1, p2, p3, t):
    u = 1 - t
    return tuple(u**3*a + 3*u*u*t*b + 3*u*t*t*c + t**3*d for a, b, c, d in zip(p0, p1, p2, p3))


def tail():
    """The curl: a centre line with a width that tapers to a point, and spines along its outer edge."""
    segments = [
        ((246, 214), (276, 224), (298, 246), (296, 266)),
        ((296, 266), (294, 288), (266, 300), (240, 298)),
        ((240, 298), (219, 296), (201, 286), (201, 270)),
        ((201, 270), (201, 262), (205, 255), (212, 249)),
    ]
    centre = []
    for s in segments:
        for k in range(24):
            centre.append(cubic(*s, k / 24))
    centre.append(segments[-1][3])
    n = len(centre)
    outer, inner = [], []
    for i, (x, y) in enumerate(centre):
        a, b = centre[max(0, i - 1)], centre[min(n - 1, i + 1)]
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy) or 1
        nx, ny = dy / length, -dx / length
        t = i / (n - 1)
        width = 7.2 * (1 - t) ** 0.7 + 1.0 * (1 - t)
        outer.append((x + nx * width, y + ny * width))
        inner.append((x - nx * width, y - ny * width))
    # Spines on the outer edge of the rising part of the tail.
    pts = []
    spine_at = {9: 7.5, 18: 6.0}
    for i, p in enumerate(outer):
        if i in spine_at:
            a, b = outer[i - 3], outer[i + 1]
            dx, dy = b[0] - a[0], b[1] - a[1]
            length = math.hypot(dx, dy)
            nx, ny = dy / length, -dx / length
            h = spine_at[i]
            pts.append(a)
            pts.append((p[0] + nx * h + dx / length * 6.5, p[1] + ny * h + dy / length * 6.5))
            pts.append(b)
        elif any(k - 3 < i < k + 2 for k in spine_at):
            continue
        else:
            pts.append(p)
    pts += list(reversed(inner))
    return "M " + " L ".join(f"{x:.2f},{y:.2f}" for x, y in pts) + " Z"


FAR_WING = """M 212,150 C 188,126 158,110 128,104
C 125,99 122,94 118,85 C 117,93 114,99 110,103
C 86,100 58,102 28,108 C 56,116 84,124 110,132
C 128,134 146,144 155,156 C 157,162 159,169 161,178 C 162,169 164,162 167,156
C 178,158 192,164 206,172 Z"""
FAR_RIBS = [
    "M 124,107 C 120,115 115,124 108,131 L 112,132 C 117,124 122,115 124,107 Z",
    "M 126,107 C 136,122 148,140 158,160 L 161,158 C 151,140 138,122 126,107 Z",
    "M 134,109 C 154,124 176,144 195,167 L 198,166 C 179,145 156,124 134,109 Z",
]
FAR_LIGHT = "M 204,149 C 184,129 158,114 130,107 C 158,117 183,132 203,152 Z"
NEAR_WING = """M 238,154 C 262,128 304,100 343,88
C 346,82 349,75 354,65 C 354,73 357,80 361,85
C 392,79 424,74 460,67 C 430,82 402,100 372,117
C 350,120 332,130 322,148 C 320,156 318,164 315,173 C 313,164 310,156 306,149
C 292,149 276,156 262,170 C 254,178 247,188 240,203 C 236,190 232,170 238,154 Z"""
NEAR_RIBS = [
    "M 350,91 C 356,99 363,108 373,116 L 370,118 C 361,110 354,100 350,91 Z",
    "M 347,92 C 336,110 325,132 316,154 L 319,155 C 328,133 339,111 347,92 Z",
    "M 338,95 C 314,110 288,134 268,162 L 271,163 C 292,136 316,112 338,95 Z",
]
NEAR_LIGHT = "M 247,150 C 272,127 306,105 343,92 C 308,108 275,130 249,153 Z"
BODY = """M 208,97
C 200,88 190,76 176,58 C 180,71 186,84 195,97
C 186,92 174,84 160,71 C 166,84 176,95 190,105
C 183,104 175,101 167,95 C 173,105 183,111 196,114
L 199,120 C 193,120 187,119 181,116 C 185,124 191,129 197,132
C 191,133 184,132 176,129 C 181,138 188,144 195,147
C 189,148 182,147 173,144 C 178,154 186,160 194,163
C 189,165 184,165 177,163 C 181,172 187,177 194,180
C 193,193 197,206 207,216
C 219,226 238,228 252,220
C 252,208 246,198 240,188
C 233,176 229,164 231,152
C 233,142 237,132 243,125
C 250,123 258,121 266,118
C 270,117 274,116 279,115
C 270,114 260,113 251,110
C 262,111 275,110 287,108
C 282,103 276,100 270,100
C 264,99 257,96 250,94
C 246,90 238,88 230,89
C 222,90 214,92 208,97 Z"""
HEAD_LIGHT = "M 213,95 C 224,91 238,90 249,95 C 238,93 225,94 214,98 Z"
EYE = "M 241,99 C 245,96 250,96 255,99 C 250,101 245,101 241,99 Z"
FORE_LEG = """M 201,174 C 206,184 212,194 211,203 C 210,209 206,214 204,219
C 205,226 205,233 202,241 C 200,236 198,231 196,228
C 195,234 192,240 186,246 C 188,240 188,234 186,229
C 182,233 177,236 170,238 C 176,233 181,227 186,220
C 190,214 193,208 194,200 C 195,191 197,182 201,174 Z"""
HIND_LEG = """M 226,197 C 238,202 252,212 253,224 C 253,232 249,238 248,244
C 254,246 261,250 269,258 C 262,255 257,254 253,255
C 255,260 255,266 253,273 C 250,267 247,263 243,261
C 241,266 238,271 232,276 C 234,270 234,265 233,260
C 229,261 225,261 219,260 C 226,257 231,253 236,246
C 238,238 237,231 233,225 C 229,218 227,207 226,197 Z"""


def svg(ground: bool, *, size=1024, scale=1.98, cx=243.0, cy=181.0, title="Draconitic Labs") -> str:
    tx, ty = size / 2 - cx * scale, size / 2 - cy * scale
    t = tail()
    defs = f"""
  <defs>
    <linearGradient id="bone" gradientUnits="userSpaceOnUse" x1="240" y1="60" x2="240" y2="305">
      <stop offset="0" stop-color="{HOT}"/><stop offset="0.45" stop-color="{RED}"/><stop offset="1" stop-color="{DEEP}"/>
    </linearGradient>
    <linearGradient id="near" gradientUnits="userSpaceOnUse" x1="305" y1="92" x2="330" y2="170">
      <stop offset="0" stop-color="{HOT}"/><stop offset="0.5" stop-color="{RED}"/><stop offset="1" stop-color="{DEEP}"/>
    </linearGradient>
    <linearGradient id="far" gradientUnits="userSpaceOnUse" x1="150" y1="100" x2="140" y2="172">
      <stop offset="0" stop-color="#f51a48"/><stop offset="0.55" stop-color="#e01240"/><stop offset="1" stop-color="#a90c31"/>
    </linearGradient>
    <radialGradient id="ground" cx="50%" cy="46%" r="62%">
      <stop offset="0" stop-color="#1c060c"/><stop offset="0.55" stop-color="#0a0406"/><stop offset="1" stop-color="#030304"/>
    </radialGradient>
    <filter id="wide" x="-40%" y="-40%" width="180%" height="180%"><feGaussianBlur stdDeviation="{34/scale:.2f}"/></filter>
    <filter id="tight" x="-20%" y="-20%" width="140%" height="140%"><feGaussianBlur stdDeviation="{9/scale:.2f}"/></filter>
    <path id="s-far" d="{FAR_WING}"/><path id="s-near" d="{NEAR_WING}"/><path id="s-body" d="{BODY}"/>
    <path id="s-fore" d="{FORE_LEG}"/><path id="s-hind" d="{HIND_LEG}"/><path id="s-tail" d="{t}"/>
    <g id="silhouette">
      <use href="#s-far"/><use href="#s-near"/><use href="#s-tail"/><use href="#s-body"/><use href="#s-fore"/><use href="#s-hind"/>
    </g>
    <!-- Dark gaps where one form passes over another, without painting the ground colour. -->
    <mask id="behind-body" maskUnits="userSpaceOnUse" x="0" y="0" width="480" height="360">
      <rect width="480" height="360" fill="#fff"/>
      <use href="#s-body" fill="#000" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>
      <use href="#s-fore" fill="#000" stroke="#000" stroke-width="2.4" stroke-linejoin="round"/>
      <use href="#s-hind" fill="#000" stroke="#000" stroke-width="2.4" stroke-linejoin="round"/>
    </mask>
    <mask id="behind-legs" maskUnits="userSpaceOnUse" x="0" y="0" width="480" height="360">
      <rect width="480" height="360" fill="#fff"/>
      <use href="#s-fore" fill="#000" stroke="#000" stroke-width="2.4" stroke-linejoin="round"/>
      <use href="#s-hind" fill="#000" stroke="#000" stroke-width="2.4" stroke-linejoin="round"/>
    </mask>
    <mask id="behind-near" maskUnits="userSpaceOnUse" x="0" y="0" width="480" height="360">
      <rect width="480" height="360" fill="#fff"/>
      <use href="#s-near" fill="#000" stroke="#000" stroke-width="2.6" stroke-linejoin="round"/>
    </mask>
  </defs>"""
    back = '<rect width="1024" height="1024" fill="url(#ground)"/>' if ground else ""
    ribs = lambda items: "".join(f'<path d="{p}" fill="#5f071b" opacity="0.8"/>' for p in items)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}" role="img" aria-label="{title}">
  <title>{title}</title>{defs}
  {back}
  <g transform="translate({tx:.2f} {ty:.2f}) scale({scale})">
    <use href="#silhouette" fill="{RED}" opacity="0.42" filter="url(#wide)"/>
    <use href="#silhouette" fill="{RED}" opacity="0.62" filter="url(#tight)"/>
    <g mask="url(#behind-body)">
      <g mask="url(#behind-near)"><use href="#s-far" fill="url(#far)"/>{ribs(FAR_RIBS)}<path d="{FAR_LIGHT}" fill="#ff7c97" opacity="0.5"/></g>
    </g>
    <g mask="url(#behind-legs)"><use href="#s-tail" fill="url(#bone)"/></g>
    <g mask="url(#behind-legs)"><use href="#s-body" fill="url(#bone)"/><path d="{HEAD_LIGHT}" fill="#ff8aa2" opacity="0.6"/></g>
    <use href="#s-near" fill="url(#near)"/>{ribs(NEAR_RIBS)}<path d="{NEAR_LIGHT}" fill="#ff8aa2" opacity="0.6"/>
    <use href="#s-fore" fill="url(#bone)"/>
    <use href="#s-hind" fill="url(#bone)"/>
    <path d="{EYE}" fill="#fff4e8"/>
  </g>
</svg>
"""


if __name__ == "__main__":
    label = sys.argv[1] if len(sys.argv) > 1 else "draft"
    (OUT / f"dragon-{label}.svg").write_text(svg(True))
    (OUT / f"dragon-{label}-transparent.svg").write_text(svg(False))
