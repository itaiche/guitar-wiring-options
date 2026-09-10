#!/usr/bin/env python3
"""Generate shop-style wiring diagrams (Seymour Duncan / StewMac convention).

Regenerate:  python3 tools/gen_diagrams.py
Outputs:     diagrams/setup{1,2,3}-*.svg
"""
import os

OUT = os.path.join(os.path.dirname(__file__), "..", "diagrams")

# --- wire colours: the actual conductor colours, not decoration -------------
WIRE = {
    "black": ("#141414", None),
    "white": ("#ffffff", "#8d8578"),   # fill, outline (white needs one)
    "red":   ("#c62828", None),
    "green": ("#1f8a3c", None),
    "bare":  ("#9a8f7a", None),
    "buss":  ("#6f6f6f", None),
    "link":  ("#3d3d3d", None),
}
INK, MUTE, FAINT = "#1a1815", "#6b6459", "#a89f92"
BODY, EDGE, PANEL = "#efece6", "#b9b1a3", "#ffffff"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


class Draw:
    def __init__(self, w, h, title, subtitle):
        self.w, self.h = w, h
        self.o = []
        self.o.append(
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'width="{w}" height="{h}" font-family="Helvetica, Arial, sans-serif">'
        )
        self.o.append(f'<rect x="0" y="0" width="{w}" height="{h}" fill="#fdfcfa"/>')
        self.text(44, 46, title, 23, INK, weight=700)
        self.text(44, 70, subtitle, 12.5, MUTE)

    # ---- primitives --------------------------------------------------------
    def text(self, x, y, s, size=12, fill=INK, weight=400, anchor="start", mono=False):
        fam = ' font-family="ui-monospace,Menlo,Consolas,monospace"' if mono else ""
        self.o.append(
            f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" '
            f'font-weight="{weight}" text-anchor="{anchor}"{fam}>{esc(s)}</text>'
        )

    def wire(self, pts, kind, width=3.0):
        fill, outline = WIRE[kind]
        d = " ".join(f"{x},{y}" for x, y in pts)
        dash = ' stroke-dasharray="7 4"' if kind == "bare" else ""
        if outline:
            self.o.append(
                f'<polyline points="{d}" fill="none" stroke="{outline}" '
                f'stroke-width="{width+2.2}" stroke-linejoin="round" stroke-linecap="round"/>'
            )
        self.o.append(
            f'<polyline points="{d}" fill="none" stroke="{fill}" stroke-width="{width}" '
            f'stroke-linejoin="round" stroke-linecap="round"{dash}/>'
        )

    def dot(self, x, y, r=5.0, fill=INK):
        self.o.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}"/>')

    def lug(self, x, y, r=6.5):
        self.o.append(
            f'<circle cx="{x}" cy="{y}" r="{r}" fill="{PANEL}" stroke="{INK}" stroke-width="2"/>'
        )

    def box(self, x, y, w, h, r=10, fill=BODY, stroke=EDGE, sw=1.8):
        self.o.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
        )

    # ---- components --------------------------------------------------------
    def pickup(self, x, y, label, leads, w=210, h=96):
        """leads: list of (colour_key, text). Returns list of exit points."""
        self.box(x, y, w, h, r=8, fill="#e8e3d9")
        self.o.append(
            f'<rect x="{x+16}" y="{y+22}" width="{w-32}" height="{h-46}" rx="4" '
            f'fill="#dcd5c8" stroke="{EDGE}" stroke-width="1.2"/>'
        )
        for i in range(6):
            cx = x + 32 + i * (w - 64) / 5
            self.o.append(f'<circle cx="{cx}" cy="{y+h/2-2}" r="5" fill="#b9b1a3"/>')
        self.text(x + w / 2, y + 17, label, 12.5, INK, 700, "middle")
        pts, n = [], len(leads)
        span = w - 60
        for i, (kind, name) in enumerate(leads):
            lx = x + 30 + (span * i / (n - 1) if n > 1 else span / 2)
            self.wire([(lx, y + h - 6), (lx, y + h + 18)], kind, 3.0)
            self.text(lx + 7, y + h + 32, name, 9, MUTE, 700, "start", mono=True)
            pts.append((lx, y + h + 18))
        return pts

    def pot(self, cx, cy, label, value, r=58):
        self.o.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{BODY}" stroke="{INK}" stroke-width="2.2"/>'
        )
        self.o.append(
            f'<circle cx="{cx}" cy="{cy}" r="{r-11}" fill="none" stroke="{EDGE}" stroke-width="1.2"/>'
        )
        self.text(cx, cy - 2, label, 12.5, INK, 700, "middle")
        self.text(cx, cy + 16, value, 11, MUTE, 400, "middle")
        ly = cy - r - 8
        self.o.append(
            f'<rect x="{cx-54}" y="{ly-3}" width="108" height="{r+11-(r-8)+14}" rx="3" '
            f'fill="{BODY}" stroke="{EDGE}" stroke-width="1.2"/>'
        )
        lugs = []
        for i, dx in enumerate((-38, 0, 38)):
            self.lug(cx + dx, ly)
            self.text(cx + dx, ly - 15, str(i + 1), 10.5, MUTE, 700, "middle")
            lugs.append((cx + dx, ly))
        return lugs  # [lug1, lug2(wiper), lug3]

    def dpdt(self, cx, top, label="DPDT  (push-pull)"):
        w, h = 160, 92
        x, y = cx - w / 2, top
        self.box(x, y, w, h, r=6, fill="#e4e0d7")
        self.text(cx, y - 9, label, 11, MUTE, 700, "middle")
        rows = []
        for ri, ry in enumerate((y + 30, y + 68)):
            row = []
            for dx in (-46, 0, 46):
                self.lug(cx + dx, ry, 6.0)
                row.append((cx + dx, ry))
            rows.append(row)
        self.text(x - 10, y + 34, "A", 11, MUTE, 700, "end")
        self.text(x - 10, y + 72, "B", 11, MUTE, 700, "end")
        return rows  # [[A1,A2,A3],[B1,B2,B3]]

    def jack(self, x, y, w=152, h=98):
        self.box(x, y, w, h, r=8, fill="#e4e0d7")
        self.text(x + w / 2, y + 24, "OUTPUT JACK", 11.5, INK, 700, "middle")
        tip = (x + 16, y + 52)
        slv = (x + 16, y + 80)
        self.lug(*tip); self.lug(*slv)
        self.text(x + 32, y + 56, "tip", 11, MUTE)
        self.text(x + 32, y + 84, "sleeve", 11, MUTE)
        return tip, slv

    def cap(self, cx, cy, label):
        self.o.append(
            f'<line x1="{cx-17}" y1="{cy-6}" x2="{cx+17}" y2="{cy-6}" stroke="{INK}" stroke-width="3"/>'
        )
        self.o.append(
            f'<line x1="{cx-17}" y1="{cy+6}" x2="{cx+17}" y2="{cy+6}" stroke="{INK}" stroke-width="3"/>'
        )
        self.text(cx + 26, cy + 5, label, 11, MUTE, 700)

    def res(self, cx, cy, label):
        self.o.append(
            f'<rect x="{cx-24}" y="{cy-9}" width="48" height="18" rx="2" '
            f'fill="{PANEL}" stroke="{INK}" stroke-width="2"/>'
        )
        self.text(cx, cy + 22, label, 10.5, MUTE, 700, "middle")

    def switch(self, x, y, w, poles, contacts, label):
        """Returns (commons, grid[pole][contact]) as coordinates."""
        rh, h = 54, 40 + poles * 54
        self.box(x, y, w, h, r=10, fill="#eae6dd")
        self.text(x + 16, y + h - 14, label, 11.5, MUTE, 700)
        cx0 = x + 46
        step = (w - 130) / contacts
        commons, grid = [], []
        for p in range(poles):
            ry = y + 40 + p * rh
            self.o.append(
                f'<line x1="{x+12}" y1="{ry}" x2="{x+w-12}" y2="{ry}" '
                f'stroke="{EDGE}" stroke-width="1" stroke-dasharray="3 5"/>'
            )
            self.lug(cx0, ry, 7.5)
            self.text(cx0, ry - 17, f"P{p+1}", 10.5, INK, 700, "middle")
            self.text(cx0 - 26, ry + 4, "C", 10.5, MUTE, 700, "end")
            commons.append((cx0, ry))
            row = []
            for c in range(contacts):
                gx = x + 116 + step * (c + 0.5)
                self.lug(gx, ry)
                row.append((gx, ry))
            grid.append(row)
        for c in range(contacts):
            gx = x + 116 + step * (c + 0.5)
            self.text(gx, y + 26, str(c + 1), 11.5, INK, 700, "middle")
        return commons, grid

    def note(self, x, y, s, size=11.5, fill=MUTE, weight=400):
        self.text(x, y, s, size, fill, weight)

    def save(self, path):
        self.o.append("</svg>")
        with open(path, "w") as f:
            f.write("\n".join(self.o))
        return path


def legend(d, x, y):
    d.note(x, y, "WIRE COLOURS  (Seymour Duncan 4-conductor code)", 11, MUTE, 700)
    items = [("black", "Black"), ("white", "White"), ("red", "Red"),
             ("green", "Green"), ("bare", "Bare shield"), ("buss", "Ground buss")]
    for i, (k, lab) in enumerate(items):
        lx = x + i * 118
        d.wire([(lx, y + 18), (lx + 30, y + 18)], k, 3.0)
        d.note(lx + 38, y + 22, lab, 11)
    d.note(x, y + 46,
           "Crossing wires are NOT connected unless a solid junction dot is shown.", 11, FAINT)


# ===========================================================================
#  SETUP 1 — "Sweep": 4-pole 5-way super switch + push-pull volume
# ===========================================================================
def setup1():
    W, H = 1300, 1310
    d = Draw(W, H, 'Setup 1 — "Sweep"',
             "4-pole 5-way super switch · push-pull volume · plain tone · RWRP pickup pair "
             "— ten voices, eight hum-cancelling")

    nk = d.pickup(100, 92, "NECK PICKUP  (screws toward nut)",
                  [("black", "NBk"), ("white", "NW"), ("red", "NR"),
                   ("green", "NG"), ("bare", "shld")])
    br = d.pickup(990, 92, "BRIDGE PICKUP  (screws toward bridge)",
                  [("black", "BBk"), ("white", "BW"), ("red", "BR"),
                   ("green", "BG"), ("bare", "shld")])
    NBk, NW, NR, NG, NSh = nk
    BBk, BW, BR, BG, BSh = br

    # hardwired coil-junction links
    LNK_N, LNK_B = (188, 250), (1068, 250)
    d.wire([NW, (NW[0], 250), LNK_N], "white", 3.0)
    d.wire([NR, (NR[0], 250), LNK_N], "red", 3.0)
    d.dot(*LNK_N)
    d.text(LNK_N[0], 272, "NW+NR link", 10.5, INK, 700, "middle", mono=True)
    d.wire([BW, (BW[0], 250), LNK_B], "white", 3.0)
    d.wire([BR, (BR[0], 250), LNK_B], "red", 3.0)
    d.dot(*LNK_B)
    d.text(LNK_B[0], 272, "BR+BW link", 10.5, INK, 700, "middle", mono=True)

    SH = 296                                   # shield lane
    d.wire([NSh, (NSh[0], SH), (1244, SH), (1244, 1160)], "bare", 3.0)
    d.wire([BSh, (BSh[0], SH)], "bare", 3.0)
    d.dot(BSh[0], SH, 4.5, WIRE["bare"][0])

    SW_X, SW_Y, SW_W = 150, 508, 980
    commons, g = d.switch(SW_X, SW_Y, SW_W, 4, 5,
                          "4-POLE 5-WAY SUPER SWITCH  ·  Fender 0992251000  ·  C = common")

    lanes = {"BG": 324, "BRBW": 348, "BBk": 372, "NBk": 396, "NRNW": 420, "NG": 444}
    off = {0: -17, 1: -6, 2: 6, 3: 17}          # per-pole drop offset

    def net(kind, lane, feed, targets, feed_from_link=None):
        """feed: pickup lead point. targets: (pole_idx, contact_idx) list."""
        ly = lanes[lane]
        xs = [g[p][c][0] + off[p] for p, c in targets]
        src = feed_from_link or feed
        lo, hi = min(xs + [src[0]]), max(xs + [src[0]])
        d.wire([(lo, ly), (hi, ly)], kind, 3.0)
        d.wire([src, (src[0], ly)], kind, 3.0)
        d.dot(src[0], ly, 4.5, WIRE[kind][0] if kind != "white" else "#8d8578")
        for p, c in targets:
            gx, gy = g[p][c]
            dx = gx + off[p]
            d.wire([(dx, ly), (dx, gy), (gx, gy)], kind, 3.0)
            d.dot(dx, ly, 4.5, WIRE[kind][0] if kind != "white" else "#8d8578")
            d.text(gx + 30, gy + 4, lane if lane in ("BG", "NG") else
                   {"BRBW": "BR/BW", "BBk": "BBk", "NBk": "NBk", "NRNW": "NR/NW"}[lane],
                   9.5, MUTE, 700, "start", mono=True)

    net("green", "BG",   BG,  [(0, 0), (0, 2), (0, 3)])
    net("red",   "BRBW", BR,  [(0, 1), (1, 0), (1, 3)], feed_from_link=LNK_B)
    net("black", "BBk",  BBk, [(1, 1), (1, 2), (3, 0)])
    net("black", "NBk",  NBk, [(0, 4), (2, 1), (2, 2)])
    net("red",   "NRNW", NR,  [(1, 4), (2, 3), (3, 1)], feed_from_link=LNK_N)
    net("green", "NG",   NG,  [(3, 2), (3, 3), (3, 4)])

    for p, c in ((2, 0), (2, 4)):
        gx, gy = g[p][c]
        d.text(gx + 30, gy + 4, "n/c", 9.5, FAINT, 400, "start")

    # ---- controls ----------------------------------------------------------
    VOL_CX, TON_CX, CY = 360, 720, 900
    vl = d.pot(VOL_CX, CY, "VOLUME", "500k audio")
    tl = d.pot(TON_CX, CY, "TONE", "500k audio")
    A, B = d.dpdt(VOL_CX, CY + 86, "DPDT push-pull  —  DOWN = series, UP = parallel")
    tip, slv = d.jack(1030, 862)
    BUSS = 1160


    # selector commons -> pots
    d.wire([commons[0], (112, commons[0][1]), (112, 800), (vl[2][0], 800), vl[2]], "link", 2.6)
    d.wire([commons[1], (88, commons[1][1]), (88, 982), (A[1][0], 982), A[1]], "link", 2.6)
    d.wire([commons[2], (64, commons[2][1]), (64, 1112), (B[1][0], 1112), B[1]], "link", 2.6)
    d.wire([commons[3], (40, commons[3][1]), (40, BUSS)], "buss", 3.4)

    # DPDT internals
    d.wire([A[0], (A[0][0], 1035), (B[1][0], 1035), B[1]], "link", 2.6)   # A1 -> B2  (series)
    d.wire([A[2], (462, A[2][1]), (462, BUSS)], "buss", 3.4)              # A3 -> gnd (parallel)
    d.wire([B[2], (492, B[2][1]), (492, 782), (vl[2][0], 782), vl[2]], "link", 2.6)  # B3 -> OUT
    d.dot(*vl[2])
    d.text(A[0][0], A[0][1] - 15, "A1 ser", 9.5, MUTE, 700, "middle")
    d.text(A[1][0], A[1][1] - 15, "A2 com", 9.5, INK, 700, "middle")
    d.text(A[2][0], A[2][1] - 15, "A3 par", 9.5, MUTE, 700, "middle")
    d.text(B[0][0], B[0][1] + 22, "B1 n/c", 9.5, FAINT, 700, "middle")
    d.text(B[1][0], B[1][1] + 22, "B2 com", 9.5, INK, 700, "middle")
    d.text(B[2][0], B[2][1] + 22, "B3 par", 9.5, MUTE, 700, "middle")

    # volume wiper -> tone + jack
    d.wire([vl[1], (vl[1][0], 760), (tl[2][0], 760), tl[2]], "link", 2.6)
    d.dot(tl[2][0], 760)
    d.wire([(tl[2][0], 760), (990, 760), (990, tip[1]), tip], "link", 2.6)
    # treble bleed
    d.cap(VOL_CX + 62, 806, "180 pF")
    d.wire([vl[1], (vl[1][0], 806), (VOL_CX + 45, 806)], "link", 2.2)
    d.wire([(VOL_CX + 79, 806), (vl[2][0], 806)], "link", 2.2)
    # tone cap
    d.cap(628, 1042, "0.022 µF")
    d.wire([tl[1], (tl[1][0], 806), (628, 806), (628, 1025)], "link", 2.6)
    d.wire([(628, 1059), (628, BUSS)], "buss", 3.4)
    d.text(tl[0][0], tl[0][1] + 26, "n/c", 10, FAINT, 400, "middle")

    # grounds
    d.wire([(VOL_CX - 58, CY), (250, CY), (250, BUSS)], "buss", 3.4)
    d.wire([(TON_CX + 58, CY), (830, CY), (830, BUSS)], "buss", 3.4)
    d.wire([slv, (996, slv[1]), (996, BUSS)], "buss", 3.4)
    d.wire([(40, BUSS), (1244, BUSS)], "buss", 4.2)
    for gx in (250, 462, 628, 830, 996, 1244):
        d.dot(gx, BUSS, 5, WIRE["buss"][0])
    d.text(1250, BUSS + 5, "", 11, MUTE)
    d.note(40, BUSS + 26,
           "GROUND BUSS — star point at the VOLUME pot casing. Both pickup shields, both pot "
           "casings, jack sleeve, selector pole 4 and DPDT A3 all land here.", 11, MUTE, 700)

    legend(d, 40, BUSS + 56)
    return d.save(os.path.join(OUT, "setup1-sweep.svg"))


# ===========================================================================
#  Shared 3-way chassis for Setups 2 and 3
# ===========================================================================
def three_way(title, sub, vol_role, tone_role, wire_fn, notes, fname):
    W, H = 1400, 1240
    d = Draw(W, H, title, sub)

    nk = d.pickup(100, 92, "NECK PICKUP  (screws toward nut)",
                  [("black", "NBk"), ("white", "NW"), ("red", "NR"),
                   ("green", "NG"), ("bare", "shld")])
    br = d.pickup(1040, 92, "BRIDGE PICKUP  (screws toward bridge)",
                  [("black", "BBk"), ("white", "BW"), ("red", "BR"),
                   ("green", "BG"), ("bare", "shld")])
    P = dict(zip(("NBk", "NW", "NR", "NG", "NSh"), nk))
    P.update(dict(zip(("BBk", "BW", "BR", "BG", "BSh"), br)))
    BUSS = 1082

    d.wire([P["NSh"], (P["NSh"][0], 262), (1330, 262), (1330, BUSS)], "bare", 3.0)
    d.wire([P["BSh"], (P["BSh"][0], 262)], "bare", 3.0)
    d.dot(P["BSh"][0], 262, 4.5, WIRE["bare"][0])

    commons, g = d.switch(470, 470, 470, 2, 3,
                          "3-WAY BLADE  ·  2-pole  ·  1 = bridge   2 = both   3 = neck")

    # bridge hot bus -> blade pole 1 contacts 1,2   |   neck hot bus -> pole 2 contacts 2,3
    BHOT, NHOT = 312, 340
    d.wire([(g[0][0][0], BHOT), (g[0][1][0], BHOT)], "green", 3.0)
    for c in (0, 1):
        d.wire([(g[0][c][0], BHOT), g[0][c]], "green", 3.0)
        d.dot(g[0][c][0], BHOT, 4.5, WIRE["green"][0])
        d.text(g[0][c][0] + 16, g[0][c][1] + 4, "BG bus", 9.5, MUTE, 700, "start", mono=True)
    d.wire([(g[1][1][0], NHOT), (g[1][2][0], NHOT)], "black", 3.0)
    for c in (1, 2):
        d.wire([(g[1][c][0], NHOT), g[1][c]], "black", 3.0)
        d.dot(g[1][c][0], NHOT, 4.5, WIRE["black"][0])
        d.text(g[1][c][0] + 16, g[1][c][1] + 4, "NBk bus", 9.5, MUTE, 700, "start", mono=True)
    d.text(g[0][2][0] + 16, g[0][2][1] + 4, "n/c", 9.5, FAINT, 400, "start")
    d.text(g[1][0][0] + 16, g[1][0][1] + 4, "n/c", 9.5, FAINT, 400, "start")

    VOL_CX, TON_CX, CY = 330, 830, 880
    vl = d.pot(VOL_CX, CY, "VOLUME", "500k audio")
    tl = d.pot(TON_CX, CY, "TONE", "500k audio")
    A, B = d.dpdt(VOL_CX, CY + 86, "DPDT — " + vol_role)
    C, E = d.dpdt(TON_CX, CY + 86, "DPDT — " + tone_role)
    tip, slv = d.jack(1150, 846)

    # blade commons -> volume input
    d.wire([commons[0], (400, commons[0][1]), (400, 806), (vl[2][0], 806), vl[2]], "link", 2.6)
    d.wire([commons[1], (424, commons[1][1]), (424, 782), (vl[2][0], 782), (vl[2][0], 806)],
           "link", 2.6)
    d.dot(vl[2][0], 806)

    # volume wiper -> tone -> jack
    d.wire([vl[1], (vl[1][0], 760), (tl[2][0], 760), tl[2]], "link", 2.6)
    d.dot(tl[2][0], 760)
    d.wire([(tl[2][0], 760), (1110, 760), (1110, tip[1]), tip], "link", 2.6)
    d.cap(TON_CX + 132, 800, "0.022 µF")
    d.wire([tl[1], (tl[1][0], 800), (TON_CX + 115, 800)], "link", 2.6)
    d.wire([(TON_CX + 149, 800), (1000, 800), (1000, BUSS)], "buss", 3.0)
    d.text(tl[0][0] - 20, tl[0][1] + 4, "n/c", 9.5, FAINT, 400, "end")

    for row, tag in ((A, "A"), (B, "B")):
        for i, pt in enumerate(row):
            d.text(pt[0], pt[1] - 14 if tag == "A" else pt[1] + 22,
                   f"{tag}{i+1}", 9, FAINT, 700, "middle")
    for row, tag in ((C, "A"), (E, "B")):
        for i, pt in enumerate(row):
            d.text(pt[0], pt[1] - 14 if tag == "A" else pt[1] + 22,
                   f"{tag}{i+1}", 9, FAINT, 700, "middle")

    ctx = dict(P=P, A=A, B=B, C=C, E=E, vl=vl, tl=tl, g=g, BUSS=BUSS,
               BHOT=BHOT, NHOT=NHOT, VOL_CX=VOL_CX, TON_CX=TON_CX)
    wire_fn(d, ctx)

    # chassis grounds
    d.wire([(VOL_CX - 58, CY), (232, CY), (232, BUSS)], "buss", 3.4)
    d.wire([(TON_CX + 58, CY), (952, CY), (952, BUSS)], "buss", 3.4)
    d.wire([slv, (1120, slv[1]), (1120, BUSS)], "buss", 3.4)
    d.wire([(60, BUSS), (1330, BUSS)], "buss", 4.2)
    for gx in (232, 952, 1000, 1120, 1330):
        d.dot(gx, BUSS, 5, WIRE["buss"][0])
    d.note(60, BUSS + 26,
           "GROUND BUSS — star point at the VOLUME pot casing.", 11, MUTE, 700)

    y = BUSS + 52
    for i, line in enumerate(notes):
        d.note(60, y + i * 17, line, 11.5, FAINT)
    legend(d, 640, BUSS + 40)
    return d.save(os.path.join(OUT, fname))


def _sp(d, ctx, pu, row_a, row_b, hot_lane, col_w, col_r, hot_x):
    """Draw one pickup's series/parallel DPDT wiring.  pu = 'N' or 'B'."""
    P, BUSS = ctx["P"], ctx["BUSS"]
    W_, R_ = P[pu + "W"], P[pu + "R"]
    # coil-junction conductors down to the DPDT
    d.wire([W_, (W_[0], col_w), (row_a[1][0], col_w), row_a[1]], "white", 3.0)   # W -> A2
    d.wire([R_, (R_[0], col_r), (row_b[1][0], col_r), row_b[1]], "red", 3.0)     # R -> B2
    d.dot(*row_a[1]); d.dot(*row_b[1])
    # A1 -> B2 jumper on the switch itself  (series link: W joins R)
    mid = (row_a[0][1] + row_b[0][1]) / 2
    d.wire([row_a[0], (row_a[0][0], mid), (row_b[1][0], mid), row_b[1]], "red", 2.6)
    # A3 -> hot bus (parallel)
    d.wire([row_a[2], (row_a[2][0] + 34, row_a[2][1]), (row_a[2][0] + 34, hot_lane),
            (hot_x, hot_lane)], "link", 2.6)
    d.dot(hot_x, hot_lane)
    # B3 -> ground (parallel)
    d.wire([row_b[2], (row_b[2][0] + 60, row_b[2][1]), (row_b[2][0] + 60, BUSS)], "buss", 3.0)
    d.dot(row_b[2][0] + 60, BUSS, 5, WIRE["buss"][0])


def setup3():
    def wiring(d, ctx):
        P, BUSS = ctx["P"], ctx["BUSS"]
        g, BHOT, NHOT = ctx["g"], ctx["BHOT"], ctx["NHOT"]
        # permanent hots and colds
        d.wire([P["BG"], (P["BG"][0], BHOT), (g[0][1][0], BHOT)], "green", 3.0)
        d.wire([P["NBk"], (P["NBk"][0], NHOT), (g[1][1][0], NHOT)], "black", 3.0)
        d.wire([P["BBk"], (P["BBk"][0], 288), (1300, 288), (1300, BUSS)], "black", 3.0)
        d.dot(1300, BUSS, 5, WIRE["buss"][0])
        d.wire([P["NG"], (P["NG"][0], 400), (72, 400), (72, BUSS)], "green", 3.0)
        # per-pickup series/parallel
        _sp(d, ctx, "B", ctx["A"], ctx["B"], BHOT, 424, 448, g[0][0][0])
        _sp(d, ctx, "N", ctx["C"], ctx["E"], NHOT, 376, 352, g[1][2][0])

    return three_way(
        'Setup 3 — "Quiet"',
        "3-way blade · one push-pull per pickup · 12 states, 8 distinct, every one hum-cancelling "
        "· Ibanez Tri-Sound on both pickups",
        "BRIDGE series / parallel", "NECK series / parallel", wiring,
        ["DOWN = coils in series (full humbucker).  UP = coils in parallel (−6 dB, brighter, still hum-cancelling).",
         "No true coil split exists anywhere in this circuit — every one of the eight voices cancels hum.",
         "Loses H4: both DPDTs are spent on the pickups, so nothing is left to series-link them."],
        "setup3-quiet.svg")


def setup2():
    def wiring(d, ctx):
        P, BUSS = ctx["P"], ctx["BUSS"]
        A, B, C, E = ctx["A"], ctx["B"], ctx["C"], ctx["E"]
        g, BHOT, NHOT = ctx["g"], ctx["BHOT"], ctx["NHOT"]
        # bridge hot to the bus; neck hot goes via the volume DPDT
        d.wire([P["BG"], (P["BG"][0], BHOT), (g[0][1][0], BHOT)], "green", 3.0)
        # volume DPDT = both humbuckers in series
        d.wire([P["NBk"], (P["NBk"][0], 400), (A[1][0] - 92, 400), (A[1][0] - 92, A[1][1]),
                A[1]], "black", 3.0)                                   # NBk -> A2 common
        d.dot(*A[1])
        d.wire([A[0], (A[0][0], NHOT), (g[1][1][0], NHOT)], "black", 2.6)   # A1 down -> blade
        d.wire([P["BBk"], (P["BBk"][0], 288), (1300, 288), (1300, 1010),
                (A[2][0] + 34, 1010), A[2]], "black", 3.0)             # BBk -> A3 up (series)
        d.wire([B[1], (B[1][0] + 74, B[1][1]), (B[1][0] + 74, BUSS)], "buss", 3.0)  # B2 -> gnd
        d.dot(B[1][0] + 74, BUSS, 5, WIRE["buss"][0])
        d.wire([(B[1][0] + 74, B[1][1]), (B[1][0], B[1][1])], "buss", 3.0)
        d.wire([P["NG"], (P["NG"][0], 424), (72, 424), (72, BUSS)], "green", 3.0)
        # tone DPDT = master coil split, one pole per pickup, through the partial taps
        d.wire([P["BW"], (P["BW"][0], 336), (C[1][0], 336), C[1]], "white", 3.0)
        d.wire([P["BR"], (P["BR"][0], 336), (C[1][0], 336)], "red", 3.0)
        d.dot(C[1][0], 336, 4.5, "#8d8578"); d.dot(*C[1])
        d.wire([P["NW"], (P["NW"][0], 360), (E[1][0], 360), E[1]], "white", 3.0)
        d.wire([P["NR"], (P["NR"][0], 360), (E[1][0], 360)], "red", 3.0)
        d.dot(E[1][0], 360, 4.5, "#8d8578"); d.dot(*E[1])
        d.res(C[2][0] + 78, C[2][1], "2.2 kΩ")
        d.wire([C[2], (C[2][0] + 54, C[2][1])], "link", 2.6)
        d.wire([(C[2][0] + 102, C[2][1]), (C[2][0] + 130, C[2][1]),
                (C[2][0] + 130, BUSS)], "buss", 3.0)
        d.dot(C[2][0] + 130, BUSS, 5, WIRE["buss"][0])
        d.res(E[2][0] + 78, E[2][1], "1.1 kΩ")
        d.wire([E[2], (E[2][0] + 54, E[2][1])], "link", 2.6)
        d.wire([(E[2][0] + 102, E[2][1]), (E[2][0] + 160, E[2][1]),
                (E[2][0] + 160, BUSS)], "buss", 3.0)
        d.dot(E[2][0] + 160, BUSS, 5, WIRE["buss"][0])

    return three_way(
        'Setup 2 — "Curated"',
        "3-way blade · both pots push-pull · ~7 distinct voices, two of which hum · "
        "buildable in an evening",
        "both humbuckers in SERIES", "master coil split (partial tap)", wiring,
        ["Volume UP lifts bridge BBk off ground and chains it to neck NBk: all four coils in series (H4, +6 dB).",
         "KNOWN LIMIT — with the volume pulled UP the neck-only position (blade 3) is SILENT, because NBk leaves the blade.",
         "  Series is a middle/bridge override, exactly as on a factory Jimmy Page harness. Setup 1 does not have this wart.",
         "Partial-tap resistors are SWITCHED IN by the tone DPDT, never soldered permanently across a coil —",
         "  a permanently bridged coil de-hum-cancels the full humbucker positions."],
        "setup2-curated.svg")


# ===========================================================================
#  Setup 1 — super-switch detail sheet
# ===========================================================================
NETS = [
    # id, colour, label, lugs [(pole, lug)] with lug 0 = common, goes-to note
    ("W1", "green", "BG",    "bridge GREEN — hot",      [(1,1),(1,3),(1,4)]),
    ("W2", "red",   "BR+BW", "bridge RED + WHITE link", [(1,2),(2,1),(2,4)]),
    ("W3", "black", "BBk",   "bridge BLACK — cold",     [(2,2),(2,3),(4,1)]),
    ("W4", "black", "NBk",   "neck BLACK — hot",        [(1,5),(3,2),(3,3)]),
    ("W5", "red",   "NR+NW", "neck RED + WHITE link",   [(2,5),(3,4),(4,2)]),
    ("W6", "green", "NG",    "neck GREEN — cold",       [(4,3),(4,4),(4,5)]),
]
COMMONS = [
    (1, "OUT bus → VOLUME lug 3"),
    (2, "→ volume DPDT  lug A2"),
    (3, "→ volume DPDT  lug B2"),
    (4, "→ GROUND buss"),
]
POLE_JOB = {1: "hot select", 2: "cold select / DPDT pole A",
            3: "second source / DPDT pole B", 4: "ground select"}


def setup1_switch():
    """Physical layout per the Oak Grigsby / Fender 4P5T manufacturer drawing:
    two rows of 12 lugs, mirrored, commons at the four outer corners.
    Top row  = pole 1 (left) + pole 2 (right):  0 5 4 3 2 1 | 5 4 3 2 1 0
    Bottom   = pole 3 (left) + pole 4 (right):  same
    Factory lug numbers 1-24: layer 1 = 1-12 (commons 1, 12),
    layer 2 = 13-24 (commons 13, 24)."""
    W, H = 1500, 1150
    d = Draw(W, H, 'Setup 1 "Sweep" — super switch, as wired',
             "Fender 0992251000 / Oak Grigsby 4-pole 5-way  ·  lug layout per the manufacturer "
             "drawing  ·  sheet 2 of 2")

    COLS, X0, XS = 12, 214, 80.0
    ROW_T, ROW_B = 432, 548
    colx = lambda c: X0 + c * XS

    def loc(pole, pos):
        """pos 0 = common. Returns (x, y, factory_lug_number)."""
        row = ROW_T if pole in (1, 2) else ROW_B
        if pole in (1, 3):
            col = 0 if pos == 0 else 6 - pos
        else:
            col = 11 if pos == 0 else 11 - pos
        base = {1: 0, 2: 0, 3: 12, 4: 12}[pole]
        return colx(col), row, base + col + 1

    # ---------------- info boxes ----------------
    d.box(44, 96, 545, 176, r=10, fill="#f2efe8")
    d.text(62, 122, "WHAT EACH POSITION GIVES YOU", 11, MUTE, 700)
    d.text(62, 146, "BLADE", 10, MUTE, 700)
    d.text(210, 146, "VOLUME DOWN — series", 10, MUTE, 700)
    d.text(400, 146, "VOLUME UP — parallel", 10, MUTE, 700)
    for i, (b, dn, up) in enumerate((
            ("1  bridge", "bridge humbucker", "bridge slug split *"),
            ("2", "outer coils in series", "outer coils parallel"),
            ("3", "both humbuckers series +6dB", "both humbuckers parallel"),
            ("4", "inner coils in series", "inner coils parallel"),
            ("5  neck", "neck humbucker", "neck screw split *"))):
        y = 168 + i * 19
        d.text(62, y, b, 10.5, INK, 700)
        d.text(210, y, dn, 10.5, INK, 400)
        d.text(400, y, up, 10.5, INK, 400)
    d.note(62, 266, "* the only two positions that hum", 9.5, FAINT, 700)

    d.box(609, 96, 400, 176, r=10, fill="#f2efe8")
    d.text(627, 122, "THE PART", 11, MUTE, 700)
    for i, line in enumerate([
            "48.2 mm long · 41 mm mounting centres",
            "#6-32 screws · 9.5 mm wafer stack",
            "24 lugs in two rows of 12.",
            "",
            "Layer 1 (lugs 1-12)  = poles 1 and 2",
            "Layer 2 (lugs 13-24) = poles 3 and 4",
            "Commons are lugs 1, 12, 13 and 24 —",
            "the four OUTER corners."]):
        d.note(627, 146 + i * 15, line, 10.5, INK if "Commons" in line else FAINT,
               700 if "Commons" in line else 400)

    d.box(1029, 96, 427, 176, r=10, fill="#f7ece2")
    d.text(1047, 122, "CONFIRM BEFORE SOLDERING", 11, MUTE, 700)
    for i, line in enumerate([
            "This is the Oak Grigsby / Fender layout.",
            "A Schaller Megaswitch M substitute uses a",
            "completely different terminal scheme —",
            "do not use this sheet for one.",
            "",
            "Meter check: a COMMON beeps to exactly one",
            "other lug in its group in every detent.",
            "Probe it and walk the lever to number the",
            "rest."]):
        d.note(1047, 146 + i * 15, line, 10.5, FAINT)

    # ---------------- switch body ----------------
    d.box(150, 392, 990, 196, r=6, fill="#e6e2d8", sw=2)
    for ex in (180, 1110):
        d.o.append(f'<circle cx="{ex}" cy="490" r="11" fill="{PANEL}" stroke="{INK}" stroke-width="2"/>')
        d.o.append(f'<circle cx="{ex}" cy="490" r="4" fill="{EDGE}"/>')
    d.o.append(f'<rect x="320" y="481" width="600" height="14" rx="4" fill="{BODY}" '
               f'stroke="{EDGE}" stroke-width="1.4"/>')
    d.text(620, 476, "actuator / lever slot", 9, FAINT, 700, "middle")
    d.o.append(f'<line x1="{colx(5)+XS/2}" y1="400" x2="{colx(5)+XS/2}" y2="580" '
               f'stroke="{EDGE}" stroke-width="1.4" stroke-dasharray="5 5"/>')

    for pole in (1, 2, 3, 4):
        for pos in range(0, 6):
            x, y, lug = loc(pole, pos)
            d.o.append(f'<rect x="{x-11}" y="{y-13}" width="22" height="26" rx="3" '
                       f'fill="{PANEL}" stroke="{INK}" stroke-width="2"/>')
            d.o.append(f'<circle cx="{x}" cy="{y}" r="4.5" fill="{BODY}" stroke="{EDGE}" stroke-width="1"/>')
            lab = "C" if pos == 0 else str(pos)
            ly = y - 20 if pole in (1, 2) else y + 28
            d.text(x - 15, ly, lab, 12, INK, 700, "end")
            d.text(x + 15, ly, f"#{lug}", 8.5, FAINT, 700, "start", mono=True)

    lgc, rgc = colx(2.5), colx(8.5)
    d.text(lgc, ROW_T + 34, "POLE 1", 12.5, INK, 700, "middle")
    d.text(rgc, ROW_T + 34, "POLE 2", 12.5, INK, 700, "middle")
    d.text(lgc, ROW_B - 24, "POLE 3", 12.5, INK, 700, "middle")
    d.text(rgc, ROW_B - 24, "POLE 4", 12.5, INK, 700, "middle")
    d.text(colx(5.5), 380, "LAYER 1  ·  lugs 1-12  ·  poles 1 + 2", 9.5, FAINT, 700, "middle")
    d.text(colx(5.5), 606, "LAYER 2  ·  lugs 13-24  ·  poles 3 + 4", 9.5, FAINT, 700, "middle")

    # ---------------- nets ----------------
    TOPB, BOTB, LEFTX, RIGHTX = 370, 618, 126, 1166
    for k, (nid, col, short, longlab, lugs) in enumerate(NETS):
        lt, lb = TOPB - k * 11, BOTB + k * 11
        tops = [loc(p, l) for p, l in lugs if p in (1, 2)]
        bots = [loc(p, l) for p, l in lugs if p in (3, 4)]
        for pts, lane, up in ((tops, lt, True), (bots, lb, False)):
            if not pts:
                continue
            for x, y, lug in pts:
                d.wire([(x, y + (-13 if up else 13)), (x, lane)], col, 3.0)
                d.dot(x, lane, 5, WIRE[col][0] if col != "white" else "#8d8578")
                d.text(x + 14, lane + (-7 if up else 13), nid, 9.5, INK, 700, "start", mono=True)
            d.wire([(min(p[0] for p in pts), lane), (max(p[0] for p in pts), lane)], col, 3.0)
        if tops and bots:
            allx = [p[0] for p in tops + bots]
            side = LEFTX if sum(allx) / len(allx) < colx(5.5) else RIGHTX
            d.wire([(min(p[0] for p in tops) if side == LEFTX else max(p[0] for p in tops), lt),
                    (side, lt), (side, lb),
                    (min(p[0] for p in bots) if side == LEFTX else max(p[0] for p in bots), lb)],
                   col, 3.0)

    # commons out
    for pole, dest, side in ((1, "→ VOL lug 3", "L"), (2, "→ DPDT A2", "R"),
                             (3, "→ DPDT B2", "L"), (4, "→ GROUND", "R")):
        x, y, lug = loc(pole, 0)
        ex = 108 if side == "L" else 1182
        d.wire([(x + (-11 if side == "L" else 11), y), (ex, y)], "link", 2.8)
        d.text(ex + (-6 if side == "L" else 6), y + 4, dest, 11, INK, 700,
               "end" if side == "L" else "start")

    # ---------------- net key ----------------
    ky = 700
    d.box(44, ky, 900, 214, r=8, fill=PANEL)
    d.text(66, ky + 26, "THE SIX NETS — lugs sharing an ID are jumpered together", 11.5, MUTE, 700)
    for lbl, x in (("ID", 122), ("WIRE", 166), ("POLE-POSITION", 370), ("FACTORY LUG #", 610),
                   ("WATCH OUT", 780)):
        d.text(x, ky + 52, lbl, 10, MUTE, 700)
    for k, (nid, col, short, longlab, lugs) in enumerate(NETS):
        y = ky + 78 + k * 22
        d.wire([(66, y - 4), (104, y - 4)], col, 3.0)
        d.text(122, y, nid, 11, INK, 700, mono=True)
        d.text(166, y, longlab, 11, INK, 400)
        d.text(370, y, "  ".join(f"P{p}-{l}" for p, l in lugs), 11, INK, 700, mono=True)
        d.text(610, y, "  ".join(f"#{loc(p, l)[2]}" for p, l in lugs), 11, INK, 700, mono=True)
        rows_used = sorted({1 if p in (1, 2) else 2 for p, _ in lugs})
        d.text(780, y, "crosses layers" if len(rows_used) > 1 else "one layer", 11,
               WIRE["red"][0] if len(rows_used) > 1 else MUTE, 700 if len(rows_used) > 1 else 400)
    d.text(66, ky + 200, "Pole 3 positions 1 and 5 (lugs #18 and #14) stay EMPTY.", 10.5, FAINT, 700)

    # ---------------- mistakes ----------------
    d.box(970, ky, 486, 214, r=10, fill="#f7e9e6")
    d.text(992, ky + 26, "THE THREE MISTAKES TO AVOID", 11, MUTE, 700)
    for i, line in enumerate([
            "1  TWO BLACKS, TWO REDS, TWO GREENS. W3 is bridge",
            "   black, W4 is neck black, and they go to different",
            "   poles. Same for reds W2/W5 and greens W1/W6.",
            "   Label every lead before it reaches the switch.",
            "2  THREE NETS CROSS BETWEEN THE TWO LAYERS —",
            "   W3, W4 and W5. Those jumpers run around the end",
            "   of the switch, not through it.",
            "3  POSITION 1 IS THE INNERMOST LUG, not the outer one.",
            "   The rows are mirrored: commons sit at the four",
            "   outer corners and the numbering counts inward."]):
        b = line[:1].isdigit()
        d.note(992, ky + 52 + i * 15, line, 10, WIRE["red"][0] if b else FAINT, 700 if b else 400)

    d.note(44, 946, "COMMONS — pole 1 (#1) → volume lug 3 · pole 2 (#12) → DPDT A2 · "
                    "pole 3 (#13) → DPDT B2 · pole 4 (#24) → ground buss.", 11.5, INK, 700)
    d.note(44, 968, "DPDT (volume push-pull):  DOWN = A2→A1 with A1 jumpered to B2 (series).   "
                    "UP = A2→A3→ground and B2→B3→OUT bus (parallel).", 11.5, MUTE)
    d.note(44, 990, "BR+BW and NW+NR are soldered together AT THE PICKUP and taped — not switched. "
                    "W2 and W5 arrive as one conductor each.", 11.5, MUTE)
    legend(d, 44, 1020)
    return d.save(os.path.join(OUT, "setup1-superswitch.svg"))



# ===========================================================================
#  Setup 1 — sheet 3: applying it to a real switch
# ===========================================================================
def setup1_build():
    W, H = 1500, 1430
    d = Draw(W, H, 'Setup 1 "Sweep" — applying it to YOUR switch',
             "Orientation, meter procedure, per-lug checklist and solder order  ·  sheet 3 of 3")

    net_of, wire_of = {}, {}
    for nid, col, short, longlab, lugs in NETS:
        for pl in lugs:
            net_of[pl] = nid
            wire_of[pl] = (col, short, longlab)
    dest = {1: "volume lug 3  (OUT bus)", 2: "volume DPDT lug A2",
            3: "volume DPDT lug B2", 4: "ground buss"}
    side = {1: "LAYER 1 · left group", 2: "LAYER 1 · right group",
            3: "LAYER 2 · left group", 4: "LAYER 2 · right group"}
    comlug = {1: 1, 2: 12, 3: 13, 4: 24}

    def factory(pole, pos):
        col = (0 if pos == 0 else 6 - pos) if pole in (1, 3) else (11 if pos == 0 else 11 - pos)
        return {1: 0, 2: 0, 3: 12, 4: 12}[pole] + col + 1

    # ---------- A: orientation ----------
    d.box(44, 96, 700, 336, r=10, fill=PANEL)
    d.text(66, 122, "A · HOW TO HOLD THE SWITCH", 11, MUTE, 700)
    bx, by, bw, bh = 90, 148, 610, 116
    d.box(bx, by, bw, bh, r=5, fill="#e6e2d8", sw=2)
    for ex in (bx + 30, bx + bw - 30):
        d.o.append(f'<circle cx="{ex}" cy="{by+bh/2}" r="9" fill="{PANEL}" stroke="{INK}" stroke-width="1.8"/>')
    d.o.append(f'<rect x="{bx+150}" y="{by+bh/2-6}" width="310" height="12" rx="3" '
               f'fill="{BODY}" stroke="{EDGE}" stroke-width="1.2"/>')
    for i in range(12):
        lx = bx + 70 + i * (bw - 140) / 11
        for yy in (by + 24, by + bh - 24):
            d.o.append(f'<rect x="{lx-7}" y="{yy-9}" width="14" height="18" rx="2" '
                       f'fill="{PANEL}" stroke="{INK}" stroke-width="1.5"/>')
    d.text(bx + bw / 2, by - 6, "lug tabs facing YOU  ·  24 of them, two rows of 12",
           10, MUTE, 700, "middle")
    d.text(bx + 30, by + bh + 18, "mounting ear", 9, FAINT, 700, "middle")
    d.text(bx + bw - 30, by + bh + 18, "mounting ear", 9, FAINT, 700, "middle")
    for i, line in enumerate([
            "Lugs toward you, mounting ears left and right, lever slot across the middle.",
            "The TOP row of 12 is layer 1 (poles 1 and 2); the BOTTOM row is layer 2 (poles 3, 4).",
            "Each row is two poles of six: a common at the OUTER end, then positions 5-4-3-2-1",
            "counting INWARD. The two position-1 lugs of a row sit next to each other in the middle.",
            "",
            "If your lugs face away from you the drawing mirrors left-to-right. That is fine —",
            "step B settles it, and step B always wins over the picture."]):
        d.note(66, 296 + i * 17, line, 11, INK if i < 4 else FAINT, 400)

    # ---------- B: meter procedure ----------
    d.box(764, 96, 692, 336, r=10, fill="#f7ece2")
    d.text(786, 122, "B · PROVE IT WITH A METER  (do this first, always)", 11, MUTE, 700)
    for i, (n, line) in enumerate([
            ("1", "Meter on continuity / beep."),
            ("",  "Probe two lugs in the same group of six."),
            ("2", "Find the four COMMONS. A common is the lug that beeps to"),
            ("",  "exactly one other lug in its group in EVERY lever position."),
            ("",  "There are four, one per group, at the outer corners."),
            ("3", "Set the blade fully toward the BRIDGE."),
            ("",  "Hold one probe on a common; find the lug that beeps."),
            ("",  "That lug is POSITION 1 of that pole. Mark it."),
            ("4", "Move the lever one detent toward the neck at a time,"),
            ("",  "marking 2, 3, 4, 5 as each lug beeps."),
            ("5", "Repeat for all four commons. Masking tape and a pen."),
            ("6", "From here on use YOUR marks, not the factory numbers."),
            ("",  "The #n numbers on sheet 2 are the manufacturer's; they"),
            ("",  "are a cross-check, not the authority. Your marks win.")]):
        d.text(786, 150 + i * 19, n, 11.5, WIRE["red"][0], 700)
        d.note(806, 150 + i * 19, line, 11, INK if n else FAINT, 700 if n else 400)

    # ---------- C: per-lug checklist ----------
    d.text(44, 466, "C · CONNECTION CHECKLIST — every one of the 24 lugs", 11.5, MUTE, 700)
    for bi, pole in enumerate((1, 2, 3, 4)):
        cx = 44 + (bi % 2) * 716
        cy = 480 + (bi // 2) * 232
        d.box(cx, cy, 696, 216, r=8, fill=PANEL)
        d.text(cx + 18, cy + 26, f"POLE {pole}", 14, INK, 700)
        d.text(cx + 90, cy + 26, side[pole], 10.5, MUTE, 700)
        d.text(cx + 18, cy + 46, f"common = your marked C  (factory #{comlug[pole]})  →  {dest[pole]}",
               10.5, INK, 700)
        for lbl, x in (("POS", 30), ("#", 78), ("NET", 128), ("SOLDER THIS", 188), ("", 640)):
            d.text(cx + x, cy + 68, lbl, 9.5, MUTE, 700)
        for pos in range(1, 6):
            y = cy + 90 + (pos - 1) * 24
            nid = net_of.get((pole, pos))
            d.text(cx + 30, y, str(pos), 12, INK, 700)
            d.text(cx + 78, y, f"#{factory(pole,pos)}", 10, FAINT, 700, mono=True)
            if nid:
                col, short, longlab = wire_of[(pole, pos)]
                d.wire([(cx + 128, y - 4), (cx + 158, y - 4)], col, 3.0)
                d.text(cx + 166, y, nid, 11, INK, 700, mono=True)
                d.text(cx + 200, y, longlab, 11, INK, 400)
            else:
                d.text(cx + 166, y, "—", 11, FAINT, 700)
                d.text(cx + 200, y, "leave EMPTY", 11, FAINT, 400)
            d.o.append(f'<rect x="{cx+650}" y="{y-11}" width="14" height="14" rx="2" '
                       f'fill="{PANEL}" stroke="{INK}" stroke-width="1.6"/>')

    # ---------- D: solder order ----------
    d.box(44, 960, 700, 300, r=10, fill=PANEL)
    d.text(66, 986, "D · SOLDER IN THIS ORDER", 11, MUTE, 700)
    for i, (n, line) in enumerate([
            ("1", "At the pickups: join bridge RED+WHITE, join neck WHITE+RED."),
            ("",  "Solder, heatshrink, done. These never reach the switch as two wires."),
            ("2", "Tin all 24 lugs you will use. Skip pole 3 positions 1 and 5."),
            ("3", "Fit the on-switch jumpers first, while access is good:"),
            ("",  "W1 across P1 1-3-4 · W2 P1-2 to P2-1 to P2-4 · W3 P2-2 to P2-3 to P4-1"),
            ("",  "W4 P1-5 to P3-2 to P3-3 · W5 P2-5 to P3-4 to P4-2 · W6 across P4 3-4-5"),
            ("4", "Now land the six pickup leads, one net at a time. Tick the boxes in C."),
            ("5", "Four commons to volume lug 3, DPDT A2, DPDT B2, ground."),
            ("6", "DPDT internals, then pots, tone cap, treble bleed, jack, ground buss."),
            ("7", "Test on the bench (panel E) BEFORE it goes in the guitar.")]):
        d.text(66, 1012 + i * 24, n, 11.5, WIRE["red"][0], 700)
        d.note(86, 1012 + i * 24, line, 11, INK if n else FAINT, 400)

    # ---------- E: test ----------
    d.box(764, 960, 692, 300, r=10, fill="#eaf2ec")
    d.text(786, 986, "E · BENCH TEST BEFORE INSTALLING", 11, MUTE, 700)
    d.note(786, 1010, "Meter across the jack tip and sleeve, volume wide open, tone wide open.",
           11, INK, 400)
    d.note(786, 1028, "Expected DC resistance, for a matched ~8 k pair:", 11, INK, 400)
    for i, (pos, dn, up) in enumerate([
            ("1", "~8 k", "~4 k"), ("2", "~8 k", "~2 k"), ("3", "~16 k", "~4 k"),
            ("4", "~8 k", "~2 k"), ("5", "~8 k", "~4 k")]):
        y = 1064 + i * 22
        d.text(806, y, f"position {pos}", 11, INK, 700)
        d.text(920, y, f"vol down {dn}", 11, MUTE)
        d.text(1050, y, f"vol up {up}", 11, MUTE)
    d.note(786, 1188, "Any position reading OPEN or near 0 Ω is a wiring fault — find it now.",
           11, WIRE["red"][0], 700)
    d.note(786, 1208, "Position 3 volume-down must be roughly double any single-pickup reading;",
           11, FAINT)
    d.note(786, 1226, "that is the proof the both-humbuckers-in-series chain is intact.", 11, FAINT)

    d.note(44, 1292, "ORIENTATION IS THE ONE THING THIS SHEET CANNOT KNOW.", 12, WIRE["red"][0], 700)
    d.note(44, 1314, "Whether position 1 sits at the left or right end depends on how the switch is "
                     "mounted. Panel B settles it in five minutes and is authoritative.", 11.5, INK)
    d.note(44, 1336, "Sheet 1 = harness overview · sheet 2 = the switch as wired · this sheet = "
                     "how to transfer it to the part in your hand.", 11.5, MUTE)
    legend(d, 44, 1364)
    return d.save(os.path.join(OUT, "setup1-build.svg"))


if __name__ == "__main__":
    for p in (setup1(), setup1_switch(), setup1_build(), setup2(), setup3()):
        print("wrote", os.path.relpath(p))
