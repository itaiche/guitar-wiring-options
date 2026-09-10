# Pole matrix — contact-by-contact verification

The verification artefact. Written before any schematic, because these failure modes are invisible
on a drawing:

- **A switch lug is not a switching node.** Everything on one lug is permanently connected. Wiring
  "bridge cold + ground" to one contact gives a *permanent* ground and silently deletes every
  series position.
- **The binding constraint on a 4P5T is contacts-per-detent (4), not poles×throws (20).**
- **Two nets sharing a pole can short during the wipe.** If the OUT bus and ground ever land on
  adjacent contacts of one pole, the guitar drops out as you move the blade.

---

## Lead naming

Seymour Duncan code. Arrows run hot-end → cold-end.

| Pickup | Screw coil | Slug coil | Series | Note |
|---|---|---|---|---|
| Neck | `NBk` → `NW` | `NR` → `NG` | `NBk` hot, `NW`+`NR` link, `NG` cold | Normal |
| Bridge | `BW` → `BBk` | `BG` → `BR` | `BG` hot, `BR`+`BW` link, `BBk` cold | **Leads reversed** |

**Why the bridge is reversed.** The pair is RWRP. Signal from a coil scales with
(magnet polarity × winding direction); hum scales with winding direction alone. Reversing the
bridge magnet inverts its signal but not its hum, so swapping its hot and ground leads puts both
humbuckers back in phase. With `pol`/`wind` as ±1:

| Coil | pol | wind | signal | hum | after lead-swap |
|---|---|---|---|---|---|
| Neck screw | +1 | +1 | +1 | +1 | — |
| Neck slug | −1 | −1 | +1 | −1 | — |
| Bridge screw | −1 | +1 | −1 | +1 | signal +1, hum −1 |
| Bridge slug | +1 | −1 | −1 | −1 | signal +1, hum +1 |

- Outer pair: signal `+2`, hum `0` ✅ · Inner pair: signal `+2`, hum `0` ✅
- Each humbucker alone: internally RWRP ✅ · Both combined: in phase ✅

A non-RWRP pair cancels on only one diagonal pair. RWRP cancels on both, which is what puts two
quack apertures on the blade instead of one.

---

## Setup 1 "Sweep" — the structural problem, and the fix

The natural formulation: the selector presents four nodes per detent, one DPDT picks
series or parallel.

```
A = element-1 hot   → OUT bus          parallel:  A→OUT, C→OUT, B→GND, D→GND
B = element-1 cold  → DPDT pole 1      series:    A→OUT, B→C,   D→GND
C = element-2 hot   → DPDT pole 2
D = element-2 cold  → GND bus
```

Four nodes, four poles. It looks like it fits — **it doesn't.** Position 3 combines two whole
humbuckers, and a whole humbucker only exists if its coil junction is linked, so it needs six
nodes: `BG`, `BBk`, `NBk`, `NG`, plus links `BR—BW` and `NW—NR`. This is why no production HH
guitar offers intra-pickup parallel *and* both-humbucker positions on one blade.

**Fix: hardwire both links, and get the second voice at positions 1 and 5 from a shorted coil
rather than a parallel one.** Those detents have a pole spare (one pickup live), so pole 3 sits
unconnected and the DPDT's parallel throw grounds the junction. Cost: positions 1-up and 5-up are
real splits and hum. The other eight voices cancel.

### The matrix

`BR—BW` and `NW—NR` are hardwired. `—` = unconnected.

| Pole | Common goes to | Pos 1 | Pos 2 | Pos 3 | Pos 4 | Pos 5 |
|---|---|---|---|---|---|---|
| **1** | OUT bus → volume lug 3 | `BG` | `BW` | `BG` | `BG` | `NBk` |
| **2** | DPDT pole 1 common | `BR` | `BBk` | `BBk` | `BR` | `NR` |
| **3** | DPDT pole 2 common | — | `NBk` | `NBk` | `NR` | — |
| **4** | GND bus | `BBk` | `NW` | `NG` | `NG` | `NG` |

Volume push-pull:

| | Pole 1 (common = selector pole 2) | Pole 2 (common = selector pole 3) |
|---|---|---|
| **DOWN** = series | → selector pole 3 common | → open |
| **UP** = parallel | → GND | → OUT bus |

Tone push-pull: **both poles spare.**

### State walk

| # | State | Path | Voice |
|---|---|---|---|
| 1 | P1 ↓ | `BG`→OUT, `BBk`→GND, `BR/BW` floating | **H1** bridge humbucker |
| 2 | P1 ↑ | `BR/BW`→GND, `BBk`→GND ⇒ screw shorted | **X1** bridge slug split *(hums)* |
| 3 | P2 ↓ | OUT←`BW`→screw→`BBk`→`NBk`→screw→`NW`→GND | **S1** outer coils series |
| 4 | P2 ↑ | `BW`,`NBk`→OUT; `BBk`,`NW`→GND | **Q1** outer coils parallel |
| 5 | P3 ↓ | `BG`→slug→`BR—BW`→screw→`BBk`→`NBk`→screw→`NW—NR`→slug→`NG`→GND | **H4** both HB series |
| 6 | P3 ↑ | `BG`,`NBk`→OUT; `BBk`,`NG`→GND | **H3** both HB parallel |
| 7 | P4 ↓ | OUT←`BG`→slug→`BR`→`NR`→slug→`NG`→GND | **S2** inner coils series |
| 8 | P4 ↑ | `BG`,`NR`→OUT; `BR`,`NG`→GND | **Q2** inner coils parallel |
| 9 | P5 ↓ | `NBk`→OUT, `NG`→GND, `NR/NW` floating | **H2** neck humbucker |
| 10 | P5 ↑ | `NR/NW`→GND, `NG`→GND ⇒ slug shorted | **X2** neck screw split *(hums)* |

### Checks

- **Contacts per detent:** 4 everywhere; positions 1 and 5 use 3. Within budget.
- **No dead states**, all ten resolve to one circuit.
- **No hot-to-ground short.** No pole carries both the OUT bus and ground, so a wiping blade can't
  bridge them. Worst case is `BG`↔`BW` (momentarily shorts the bridge slug) — silent.
- **Volume and tone in circuit in all ten states.**
- **Dangling coils left open, not shorted.** A shorted coil on a shared magnet structure damps the
  live one through eddy-current loading and audibly dulls it; an open one only adds stray capacitance.
- **Shared nets check out.** `BR/BW` appears on P1c2, P2c1 and P2c4; `NW/NR` on P2c5, P3c4 and P4c2.
  Each was walked in all ten states — no unintended path.
- **Split choice.** Pos 1-up gives the bridge **slug** (inner) coil, 17 mm further from the bridge
  and the warmer of the two. Pos 5-up gives the neck **screw** (outer) coil — the woollier one;
  reaching the brighter slug would collide with pole 1's assignment in that detent. Accepted.
- **No partial taps.** The only insertion point is the DPDT's UP throw to ground, which is also the
  cold return in positions 2–4 — a resistor there would sit in the signal path in six other states.

---

## Setup 2 "Curated" — 3-way blade + 2 push-pulls

**Why not a standard 2-pole 5-way.** Both poles are consumed just selecting the pickup:

```
Pole A common → OUT,  contacts 1,2,3 = BG
Pole B common → OUT,  contacts 3,4,5 = NBk
```

Nothing is left to route a coil junction, so positions 1 and 2 are identical, and so are 4 and 5.
This is why PRS uses a proprietary blade and Fender the 4-pole super switch.

| Control | Function | Poles |
|---|---|---|
| 3-way blade | bridge / both / neck | 2 |
| Volume push-pull | both humbuckers in series (H4) | 2 |
| Tone push-pull | master coil split, through the partial taps | 2 |

Series link: pole A common = `NBk`; down → blade, up → `BBk`. Pole B common = `BBk`; down → ground,
up → open.

> **Known limit.** With the volume pulled UP, the neck-only position is **silent** — `NBk` leaves
> the blade, and only `BG` is on the bus in positions 1 and 2. Series is a middle/bridge override,
> exactly as on a factory Jimmy Page harness. Setup 1 does not have this wart.

---

## Setup 3 "Quiet" — 3-way blade + per-pickup series/parallel

Both DPDTs are spent on the pickups, so nothing is left to series-link them — hence a 3-way blade,
not a 4P5T, and no H4.

Per-pickup DPDT (bridge; neck is the mirror):

| | Pole A (common = `BW`) | Pole B (common = `BR`) |
|---|---|---|
| **DOWN** = series | → `BR` | → open |
| **UP** = parallel | → bridge hot bus | → GND |

`BG` permanently on the hot bus, `BBk` permanently grounded.

12 states, **8 distinct**, all hum-cancelling:

| Blade | V↓ T↓ | V↑ T↓ | V↓ T↑ | V↑ T↑ |
|---|---|---|---|---|
| Bridge | H1 | P1 | *dup* | *dup* |
| Both | H3 | bridge-∥ + neck-series | bridge-series + neck-∥ | both parallel |
| Neck | H2 | *dup* | P2 | *dup* |

No true split exists, so nothing hums — and nothing barks like a real single coil either.
