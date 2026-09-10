# Wiring spec — 2× humbucker, 1 volume, 1 tone, 1 selector

**Guitar.** Semi-hollow LP-style (mahogany, maple top, upper-bout f-hole), ESP 24-fret maple neck /
ebony board, TOM + stop bar. Rear control cavity. Blade slot already routed. Two custom-wound
PAF-class humbuckers, 4-conductor + bare shield — **spec still open**, which is the most useful
fact here.

**Answer.** A 4-pole 5-way super switch, a push-pull volume that means one thing everywhere, a
plain tone pot, and an RWRP pickup pair: ten voices, eight dead quiet.
[Setup 1](#setup-1--sweep-recommended) · verification in [docs/pole-matrix.md](docs/pole-matrix.md).

---

## 1. The one decision that changes everything: RWRP

Two coils cancel hum only if they are reverse-wound **and** reverse-polarity relative to each
other. Inside one humbucker that is always true. Across two pickups it depends on how the pair was
built:

| Pair | Which coil pairs cancel | Result |
|---|---|---|
| **Non-RWRP** (identical pickups — the default) | Diagonal only: neck screw + bridge slug | One quiet quack aperture (~90 mm). What PRS ships. |
| **RWRP** (bridge magnet reversed) | Outer+outer **and** inner+inner | **Two** quiet apertures (~107 mm, ~73 mm) |

Since the pickups are being wound to order, RWRP is free and strictly better — one extra usable
voice for one instruction to the winder. The only consequence: the bridge's hot and ground leads
swap, to keep the humbuckers in phase. Sign algebra in
[docs/pole-matrix.md](docs/pole-matrix.md#lead-naming).

> **Setups 1 and 3 assume the RWRP spec** in [§6](#6-pickup-specification); Setup 1 requires it —
> with a conventional pair its positions 2 and 4 hum. **Setup 2 is the exception:** grounding a coil
> junction always leaves the coil next to the hot lead, so its master split resolves to the
> *diagonal* pair, which cancels only with a conventional pair. Setups 1 and 2 cannot both be built
> from one set of pickups.

## 2. Option taxonomy

Output relative to one humbucker. Hum assumes coils matched within ~10% DCR — cancellation quality
scales with that match.

| ID | Sound | Circuit | Hum | Output | Reference |
|---|---|---|---|---|---|
| **H1** | Bridge humbucker | bridge coils in series | ✅ | 0 dB (ref) | LP bridge — AC/DC, Slash |
| **H2** | Neck humbucker | neck coils in series | ✅ | 0 dB (+2 perceived) | LP neck — Clapton "Beano" |
| **H3** | Both HB parallel | classic middle | ✅ | ~0 to −1 dB | LP middle — Duane Allman |
| **H4** | Both HB **series** | 4 coils in series | ✅ | +6 dB nom, +4.5 perceived | Jimmy Page series pull |
| **P1** | Bridge coils parallel | — | ✅ | −6 dB | Ibanez Tri-Sound; Lifeson Axcess |
| **P2** | Neck coils parallel | — | ✅ | −6 dB | Ibanez Tri-Sound |
| **Q1** | **Outer coils parallel** | neck screw + bridge screw, ~107 mm | ✅ *RWRP* | −6 dB | PRS Custom 24 pos 4; EBMM Axis pos 2 |
| **Q2** | Inner coils parallel | neck slug + bridge slug, ~73 mm | ✅ *RWRP* | −6 dB | Ibanez AZ / RG pos 4 |
| **Q3** | Diagonal parallel | neck screw + bridge slug, ~90 mm | ✅ *non-RWRP* | −6 dB | PRS Custom 24 factory pos 4 |
| **S1** | **Outer coils series** | two singles in series, wide | ✅ *RWRP* | 0 dB | Schaller HH3 |
| **S2** | Inner coils series | ~73 mm, series | ✅ *RWRP* | 0 dB | Free-Way 3X3-04 |
| **X1** | Bridge split | one coil alone | ❌ | −6 dB (−4 tapped) | PRS McCarty 594 |
| **X2** | Neck split | one coil alone | ❌ | −6 dB (−4 tapped) | Gibson LP Modern |
| **M1** | Neck HB + bridge single | full neck ∥ one bridge coil | ❌ | −3.5 dB | PRS Custom 24 pos 2 |

Three things worth knowing:

- **Parallel (P1/P2) is the hum-free alternative to a split.** Same −6 dB and the same brightening —
  inductance drops 4×, so the resonant peak climbs about an octave — but the coils stay paired, so
  hum still cancels. Ibanez shipped this as Tri-Sound in 1978.
- **Two split coils in *series* (S1/S2) sit at full output.** Same turn count as a humbucker, but
  coils 73–107 mm apart have no mutual inductance: humbucker level, single-coil clarity.
- **H4 is the one great Page extra.** +6 dB, mid-forward, the best passive front-end boost available.

### Excluded

| Excluded | Why |
|---|---|
| Out-of-phase humbucker pair | Thin, −4 dB, one-trick. Tiring with only five detents. |
| Two coils of one humbucker out of phase | Near-total cancellation. A fault, not a sound. |
| Series + out-of-phase | Louder version of the same problem. |
| Varitone / notch filters | Needs a rotary we don't have. |
| "Greeny" magnet flip | Permanent, and compromises every other position. |

**Q1/Q2 and Q3 are mutually exclusive** — the RWRP fork from §1, not a menu.

## 3. How the vendors solve this

| Vendor / model | Controls | Delivers | Takeaway |
|---|---|---|---|
| Gibson LP Modern | 2 vol, 2 tone, push-pull splits | H1–H3, X1, X2 | Splits on push-pulls; partial taps soften them |
| Gibson "Jimmy Page" | 4 push-pulls | splits, phase, H4 | Keep H4; drop phase — dead in two of three detents |
| PRS Custom 24 | 5-way blade | H1, M1, H3, Q3, H2 | The **position ordering**: humbuckers at the ends, quack in the middle |
| PRS McCarty 594 | 3-way + 2 push-pull splits | H1–H3, X1, X2 | Asymmetric partial taps, 1.1k neck / 2.2k bridge |
| Ibanez Tri-Sound | 3-way + per-pickup mini-toggle | H1–H3, P1, P2, X1, X2 | **Parallel instead of split** |
| Ibanez AZ / RG 5-way | 5-way blade | H1, Q2, H3, P2, H2 | Inner-coil combinations |
| EBMM Axis | 5-way | H1, Q1, H3, Q2, H2 | Both quack apertures on one blade |
| Yamaha Revstar | 3-way + "Dry Switch" | passive low-cut | Tone shaping is orthogonal to selection — but see below |

**Three traps this survey exposed:**

1. **A Switchcraft 3-way toggle contributes zero switching poles.** Two SPST sections bonded to one
   common output lug: it gates hots, it cannot route a coil. "Toggle + 2 push-pulls" is a 4-pole
   budget, not 6.
2. **A standard 2-pole 5-way cannot express an HH map** — both poles go to pickup selection. Hence
   PRS's proprietary blade and Fender's 4-pole super switch.
   [Reasoning](docs/pole-matrix.md#why-not-a-standard-2-pole-5-way).
3. **The copied Revstar "Dry Switch" values are wrong.** 330 kΩ ∥ 3300 pF corners at **146 Hz**, not
   ~3 kHz (`f = 1/2πRC`). For a low-mid cut use ~470 kΩ ∥ 680 pF upstream of the volume pot — and
   measure it.

## 4. The three setups

### Setup 1 — "Sweep" (recommended)

4P5T super switch + push-pull volume + plain tone.

| Blade | Volume DOWN — *series* | Volume UP — *parallel* |
|---|---|---|
| 1 (bridge) | **H1** bridge humbucker | **X1** bridge slug split ⚠️ hums |
| 2 | **S1** outer coils series | **Q1** outer coils parallel |
| 3 | **H4** both HB series, +6 dB | **H3** both HB parallel |
| 4 | **S2** inner coils series | **Q2** inner coils parallel |
| 5 (neck) | **H2** neck humbucker | **X2** neck screw split ⚠️ hums |

The push-pull means one thing in every detent: **down adds series, up goes parallel** — no
per-position exceptions, which is where most multi-push-pull harnesses fail. Read the columns and
you get two coherent guitars: down is the loud one, up is the bright one. Levels within each row
are close enough to switch mid-song.

The tone push-pull is **unused** — both poles spare. Leave it plain.

**Limits.** No partial taps (the only insertion point is shared with six other states). Positions
1-up and 5-up are true splits and hum. No M1.

**Risk.** The naive version doesn't fit — position 3 needs six nodes against four poles. Resolution
and the ten-state walk are in
[docs/pole-matrix.md](docs/pole-matrix.md#setup-1-sweep--the-structural-problem-and-the-fix). Don't
deviate from that table without re-walking it.

### Setup 2 — "Curated"

3-way blade + both push-pulls. ~7 distinct voices, two of which hum. Nothing subtle can go wrong.

| Control | Function |
|---|---|
| 3-way blade | bridge / both / neck → H1, H3, H2 |
| Volume push-pull | both humbuckers in series → **H4** |
| Tone push-pull | master coil split → **X1**, **X2**, both-split parallel |

> **Known limit.** With the volume pulled UP the neck-only position is **silent** — the neck hot
> leaves the blade, so series is a middle/bridge override, exactly as on a factory Jimmy Page
> harness. Setup 1 does not have this wart.

For when you want it playable this weekend.

### Setup 3 — "Quiet"

3-way blade + one push-pull per pickup. 12 states, **8 distinct, all hum-cancelling.** No true split
anywhere — Ibanez Tri-Sound on both pickups.

| Blade | V↓ T↓ | V↑ T↓ | V↓ T↑ | V↑ T↑ |
|---|---|---|---|---|
| Bridge | H1 | P1 | *dup* | *dup* |
| Both | H3 | bridge-∥ + neck-series | bridge-series + neck-∥ | both parallel |
| Neck | H2 | *dup* | P2 | *dup* |

Loses H4 — both DPDTs are spent on the pickups, leaving nothing to series-link them. For high gain
or a room with bad mains.

### Choosing

Widest range and careful building → **1**. Working by Sunday → **2**. Noisy room → **3**.

## 5. Shared build details

| Item | Value | Why |
|---|---|---|
| Volume pot | 500 kΩ audio, CTS 450S push-pull | 250k audibly dulls a humbucker |
| Tone pot | 500 kΩ audio | Setup 1 plain; Setups 2–3 push-pull |
| Shaft | Long bushing (¾" / 19 mm) | Mandatory through a carved cap |
| Tone cap | 0.022 µF film, 200 V+ | Gibson value for 500k + humbucker |
| Treble bleed | 180 pF alone (PRS), or 680 pF + 150 kΩ series | Don't stack a bleed on '50s wiring |
| Topology | Modern, not '50s | '50s + bleed over-brightens |
| Grounding | Single star point at the volume pot | Long runs in a semi-hollow; a loop hums more than any split |
| Shielding | Copper foil, bonded at the star point only | Coil junctions are live signal nodes in several states |
| Hookup | Single-core shielded for pickup runs | Same reason |
| Jack | Switchcraft #11 mono | — |

**Partial taps** (1.1 kΩ neck / 2.2 kΩ bridge) apply to **Setup 2 only**, and must be *switched in*.
Permanently bridging a coil de-hum-cancels the full humbucker positions — a common, well-hidden
mistake.

**Semi-hollow note.** The f-hole makes this more feedback-prone at high gain. The fix is the
wax-potting spec, not the wiring.

## 6. Pickup specification

Send this to the winder verbatim.

> Two 4-conductor humbuckers with a **separate bare shield** (not tied to a coil lead internally),
> PAF class, 7.5–8.5 kΩ.
>
> 1. **Matched pair** — per-coil DCR within 10% across the two pickups. Cancellation in the combined
>    positions scales with this; it is the usual reason a "hum-cancelling" position still hums.
> 2. **RWRP pair** — bridge magnet reversed relative to neck, so bridge screw and neck screw are
>    opposite polarity.
> 3. **Seymour Duncan colour code** — Black = north start, White = north finish, Red = south finish,
>    Green = south start, bare = shield.
> 4. **Document per pickup** — which lead pair is the screw coil and which the slug, each coil's
>    magnet orientation, each coil's measured DCR.
> 5. Mount **screws-out**: poles toward the nut on the neck, toward the bridge on the bridge.

**Go / no-go before closing the cavity:**

1. Hold the pickups face to face — an RWRP pair **attracts**. If they repel, positions 2 and 4 will
   hum; stop and call the winder.
2. Meter each coil; confirm all four within 10%.
3. Confirm the bare shield is isolated from all four conductors.

## 7. Verification

1. **Re-walk the pole matrix on paper.** Every fatal flaw found while designing this was a
   contact-level error invisible on a schematic.
2. **Meter the switch** — rock the blade slowly with an ohmmeter across the OUT bus and ground, both
   push-pull states, confirming it never shorts mid-wipe.
3. **Breadboard outside the guitar** and audition all ten states first. Re-soldering a 24-lug switch
   twice is not fun.
4. **Measure any filter network** you add — see trap 3 in §3.

## Repo

Published at **[itaiche.github.io/guitar-wiring-options](https://itaiche.github.io/guitar-wiring-options/)**
— everything below, plus a live circuit explorer, on one page.

| File | What |
|---|---|
| [index.html](index.html) | The GitHub Pages site: this document plus the interactive explorer |
| [spec.md](spec.md) | This document |
| [docs/pole-matrix.md](docs/pole-matrix.md) | Contact-by-contact verification. Read before soldering. |
| [bom.md](bom.md) | Parts and prices |
| [diagrams/](diagrams/) | Shop-style wiring diagrams |
| [tools/gen_diagrams.py](tools/gen_diagrams.py) | Regenerates the diagrams |

## Provenance

Vendor survey and coil theory: a 24-agent research → design → adversarial-review pass (7
researchers, 4 candidate designs, 12 reviewers on electrical validity, hum/phase and musical
usefulness). The Setup 1 matrix is my own, derived after all four candidates failed electrical
review; verified on paper, **not yet on a bench**. §3's position maps carry citations in the
research but I have not opened every primary source — background, not engineering.
