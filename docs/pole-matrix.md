# Pole matrix — contact-by-contact verification

This is the verification artefact. It is written **before** any schematic, because the failure
modes it catches are invisible on a pretty diagram:

- **A switch lug is not a switching node.** Everything soldered to one lug is permanently
  connected to everything else on that lug. Wiring "bridge cold + ground" to one contact does not
  give you a switched ground — it gives you a permanent one, and silently deletes every series
  position downstream.
- **The binding constraint on a 4P5T switch is contacts-per-detent (4), not poles-times-throws
  (20).** A design can pass a pole count and still need five simultaneous connections in one detent.
- **Two nets that share a pole can short during the wipe** between detents. If the OUT bus and
  ground ever appear on adjacent contacts of the same pole, the guitar clicks or drops out when you
  move the blade.

Every state below was walked node by node.

---

## Lead naming

Seymour Duncan colour code, which is what we are specifying to the winder.

| Pickup | Screw coil | Slug coil | Series config | Notes |
|---|---|---|---|---|
| Neck | `NBk` → `NW` | `NR` → `NG` | `NBk` hot, `NW`+`NR` link, `NG` cold | Normal SD wiring |
| Bridge | `BW` → `BBk` | `BG` → `BR` | `BG` hot, `BR`+`BW` link, `BBk` cold | **Leads reversed** — see below |

Arrows point hot-end → cold-end, i.e. the direction the chain runs toward ground.

**Why the bridge is reversed.** The pair is specified RWRP: the bridge magnet is reversed relative
to the neck. Signal from a coil scales with (magnet polarity × winding direction); hum scales with
winding direction alone. Reversing the bridge magnet inverts its string signal but not its hum, so
the two humbuckers would fight each other in the combined positions. Swapping the bridge's hot and
ground leads re-inverts the signal and lands both pickups in phase.

Working the algebra with `pol`/`wind` as ±1, signal `= pol × wind`, hum `= wind`:

| Coil | pol | wind | signal | hum | after bridge lead-swap |
|---|---|---|---|---|---|
| Neck screw | +1 | +1 | +1 | +1 | — |
| Neck slug | −1 | −1 | +1 | −1 | — |
| Bridge screw | −1 | +1 | −1 | +1 | signal +1, hum −1 |
| Bridge slug | +1 | −1 | −1 | −1 | signal +1, hum +1 |

- Outer pair (neck screw + bridge screw): signal `+1 +1 = +2`, hum `+1 −1 = 0` ✅
- Inner pair (neck slug + bridge slug): signal `+1 +1 = +2`, hum `−1 +1 = 0` ✅
- Each humbucker alone: internally RWRP, cancels regardless ✅
- Both humbuckers combined: both now signal-positive, in phase ✅

This is the payoff for specifying the pickups. A conventional non-RWRP pair cancels on only *one*
diagonal coil pair; the RWRP pair cancels on **both** the outer and the inner pair, which is what
puts two distinct quack apertures on the blade instead of one.

---

## Setup 1 "Sweep" — the structural problem, and the fix

The natural formulation is: the selector presents four nodes per detent and one DPDT decides
series-or-parallel.

```
A = element-1 hot    → OUT bus
B = element-1 cold   → volume-DPDT pole 1 common
C = element-2 hot    → volume-DPDT pole 2 common
D = element-2 cold   → GND bus

parallel:  A→OUT, C→OUT, B→GND, D→GND
series:    A→OUT, B→C,   D→GND
```

That is exactly 4 nodes, and the switch has exactly 4 poles. It looks like it fits.

**It does not.** Position 3 combines the two whole humbuckers, and a whole humbucker only exists if
its coil junction is linked. Position 3 therefore needs six nodes: `BG`, `BBk`, `NBk`, `NG`, plus
the links `BR—BW` and `NW—NR`. Six into four does not go. This is the conflict that sinks the naive
version, and it is the reason no production HH guitar offers intra-pickup parallel *and*
both-humbuckers positions on one blade.

**The fix: hardwire both coil-junction links, and reach the second voice at positions 1 and 5 with
a shorted coil instead of a parallel one.** Positions 1 and 5 have a pole spare (only one pickup is
live), so pole 3 sits unconnected there and the DPDT's parallel throw grounds the junction — which
shorts one coil and leaves a true single coil.

The cost is honest and stated in the spec: positions 1-up and 5-up are real splits and they hum.
The other eight voices are hum-cancelling.

### The matrix

`BR—BW` and `NW—NR` are hardwired links. `—` means the contact is left unconnected.

| Pole | Common goes to | Pos 1 | Pos 2 | Pos 3 | Pos 4 | Pos 5 |
|---|---|---|---|---|---|---|
| **1** | OUT bus → volume lug 3 | `BG` | `BW` | `BG` | `BG` | `NBk` |
| **2** | Volume-DPDT pole 1 common | `BR` | `BBk` | `BBk` | `BR` | `NR` |
| **3** | Volume-DPDT pole 2 common | — | `NBk` | `NBk` | `NR` | — |
| **4** | GND bus | `BBk` | `NW` | `NG` | `NG` | `NG` |

Volume push-pull (DPDT):

| | Pole 1 (common = selector pole 2) | Pole 2 (common = selector pole 3) |
|---|---|---|
| **DOWN** = series | → selector pole 3 common | → open |
| **UP** = parallel | → GND | → OUT bus |

Tone push-pull: **both poles spare.**

### State walk — all ten

| # | State | Path | Voice |
|---|---|---|---|
| 1 | P1 down | `BG`→OUT, `BBk`→GND, `BR/BW` floating, link intact | **H1** bridge humbucker |
| 2 | P1 up | `BR/BW`→GND, `BBk`→GND ⇒ screw coil shorted; `BG`→slug→gnd | **X1** bridge slug split *(hums)* |
| 3 | P2 down | OUT←`BW`→screw→`BBk`→`NBk`→screw→`NW`→GND | **S1** outer coils in series |
| 4 | P2 up | `BW`,`NBk`→OUT; `BBk`,`NW`→GND | **Q1** outer coils parallel |
| 5 | P3 down | `BG`→slug→`BR—BW`→screw→`BBk`→`NBk`→screw→`NW—NR`→slug→`NG`→GND | **H4** both HB series, +6 dB |
| 6 | P3 up | `BG`,`NBk`→OUT; `BBk`,`NG`→GND | **H3** both HB parallel |
| 7 | P4 down | OUT←`BG`→slug→`BR`→`NR`→slug→`NG`→GND | **S2** inner coils in series |
| 8 | P4 up | `BG`,`NR`→OUT; `BR`,`NG`→GND | **Q2** inner coils parallel |
| 9 | P5 down | `NBk`→OUT, `NG`→GND, `NR/NW` floating, link intact | **H2** neck humbucker |
| 10 | P5 up | `NR/NW`→GND, `NG`→GND ⇒ slug coil shorted; `NBk`→screw→gnd | **X2** neck screw split *(hums)* |

### Checks

- **Contacts per detent:** 4, 4, 4, 4, 4 — pos 1 and 5 use only 3 (pole 3 unconnected). Within budget.
- **No dead states.** All ten resolve to exactly one circuit with a path from a coil to OUT.
- **No hot-to-ground short.** No pole carries both the OUT bus and ground on any contact, so a
  wiping blade cannot bridge them. Worst case on pole 1 is `BG`↔`BW` (momentarily shorts the bridge
  slug coil) and `BG`↔`NBk` (momentarily parallels the two hots) — both silent.
- **Volume and tone in circuit in all ten states.** OUT bus feeds volume lug 3 unconditionally.
- **Dangling coils are left open, not shorted.** In positions 2 and 4 the unused coils hang off one
  end with the far end floating. Deliberate: a *shorted* coil on a shared magnet structure damps the
  live coil through eddy-current loading and audibly dulls it; an open one only adds a little stray
  capacitance.
- **Split-coil selection.** Pos 1-up gives the bridge **slug** (inner) coil — the warmer of the two
  and the right choice, 17 mm further from the bridge than a screw-coil split. Pos 5-up gives the
  neck **screw** (outer, nut-side) coil, which is the woollier of the two neck coils. Getting the
  brighter neck slug instead would need `NBk` grounded and `NR` hot, which collides with pole 1's
  assignment in position 5. Accepted; noted in the spec.
- **Partial-tap resistors are not used here.** The only place to insert one is the DPDT's UP throw
  to ground, and that same throw is the cold return for positions 2, 3 and 4 — a resistor there
  would sit in series with the signal in six other states. Permanently bridging a coil instead
  would de-hum-cancel the full-humbucker positions. So: no partial taps in Setup 1.

---

## Setup 2 "Curated" — 3-way blade + 2 push-pulls

### Why not a standard 2-pole 5-way

A garden-variety CRL/Oak 5-way is 2 poles. Both are consumed just selecting which pickup reaches
the output:

```
Pole A common → OUT,  contacts 1,2,3 = BG    (bridge live in 1,2,3)
Pole B common → OUT,  contacts 3,4,5 = NBk   (neck live in 3,4,5)
```

Nothing is left to route a coil junction, so every extra voice must come from the
position-independent push-pulls — which means positions 1 and 2 are identical, and so are 4 and 5.
A 2-pole 5-way cannot express a real HH map. This is precisely why PRS uses a proprietary blade,
Fender uses the 4-pole super switch, and Schaller sells purpose-built Megaswitches. Do not buy a
standard 5-way for an HH guitar and expect the PRS map.

So Setup 2 uses a **3-way blade** in the same slot.

| Control | Function | Poles |
|---|---|---|
| 3-way blade | bridge / both / neck | 2 |
| Volume push-pull | both humbuckers in series (H4) | 2 |
| Tone push-pull | master coil split, both pickups | 2 |

Blade: pole A common → OUT, contacts 1,2 = `BG`. Pole B common → OUT, contacts 2,3 = `NBk`.
Grounds hardwired. Coil junctions hardwired for the humbucker case, lifted by the tone DPDT.

Voices: H1, H3, H2, H4, X1, X2, and both-split-parallel — about 7 distinct, two of which hum.
Buildable in an evening; nothing subtle can go wrong.

---

## Setup 3 "Quiet" — 3-way blade + per-pickup series/parallel

Both DPDTs are spent on the two pickups, one each, so there is no DPDT left to combine the pickups
in series — which is why this one drops H4 and uses a 3-way blade rather than a 4P5T.

| Control | Function | Poles |
|---|---|---|
| 3-way blade | bridge / both / neck | 2 |
| Volume push-pull | bridge coils series ↔ parallel | 2 |
| Tone push-pull | neck coils series ↔ parallel | 2 |

Per-pickup series/parallel DPDT (bridge shown; neck is the mirror with `NBk` hot / `NG` ground):

| | Pole 1 (common = `BW`) | Pole 2 (common = `BR`) |
|---|---|---|
| **DOWN** = series | → `BR` | → open |
| **UP** = parallel | → bridge hot bus | → GND |

`BG` permanently on the bridge hot bus, `BBk` permanently grounded.

12 reachable states, **8 distinct**, every one hum-cancelling:

| Blade | Vol down / Tone down | Vol up / Tone down | Vol down / Tone up | Vol up / Tone up |
|---|---|---|---|---|
| Bridge | H1 | P1 | H1 *(dup)* | P1 *(dup)* |
| Both | H3 | bridge-∥ + neck-series | bridge-series + neck-∥ | both parallel |
| Neck | H2 | H2 *(dup)* | P2 | P2 *(dup)* |

This is the Ibanez Tri-Sound idea applied to both pickups. No true split exists anywhere, so
nothing hums — and nothing barks like a real single coil either.
