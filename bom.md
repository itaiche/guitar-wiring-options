# Bill of materials

Prices are indicative USD, mid-2026, before shipping. Where a part is hard to source, a verified
substitute is listed.

## Setup 1 — "Sweep" (recommended)

| # | Part | Spec | Part number | ~Price |
|---|---|---|---|---|
| 1 | Pickup selector | 4-pole 5-way "Super Switch", 24 lugs, two wafers | Fender 0992251000 · Allparts EP-0078-000 · StewMac I-3200 | $21–35 |
| | *substitute* | 4P5T, slimmer PCB body | Schaller Megaswitch M, art. 15310006 | ~$22 |
| 1 | Volume pot | CTS 450S DPDT push-pull, 500 kΩ audio, **¾" long bushing** | StewMac #0229 (450S 3912) | ~$13 |
| 1 | Tone pot | CTS 500 kΩ audio, plain, long bushing | CTS 450S 3912 (no switch) | ~$8 |
| 1 | Tone capacitor | 0.022 µF film, 200 V+ | Orange Drop 715P · Mallory 150 | $2–5 |
| 1 | Treble bleed cap | 180 pF silver mica (PRS value) | — | ~$1 |
| | *alternative* | 680 pF + 150 kΩ ¼ W in series (Tone Saver) | — | ~$2 |
| 1 | Output jack | Mono ¼", long-frame | Switchcraft #11 | ~$5 |
| 2 | Knobs | To taste, split-shaft for the push-pull | — | $10–30 |
| — | Hookup wire | Single-core shielded, pickup runs | Gavitt · Mogami | ~$10 |
| — | Cavity shielding | Copper foil tape, adhesive conductive | — | ~$12 |
| — | Solder | 60/40 rosin core, 0.8 mm | — | ~$8 |

**Subtotal, harness only: ~$90–120.**

> ⚠️ The super switch is a **two-wafer** part. Confirm ≥34 mm (ideally 36.5 mm) of clearance under
> the blade slot before ordering. The rear cavity makes this likely but measure it.

## Setup 2 — "Curated"

| # | Part | Spec | Part number | ~Price |
|---|---|---|---|---|
| 1 | Pickup selector | 3-way blade, 2-pole | Oak Grigsby / CRL 3-way | ~$12 |
| 2 | Pots | CTS 450S DPDT push-pull, 500 kΩ audio, long bushing | StewMac #0229 | ~$26 |
| 1 | Tone capacitor | 0.022 µF film | Orange Drop 715P | $2–5 |
| 1 | Partial-tap resistor, neck | 1.1 kΩ ¼ W metal film | PRS value | <$1 |
| 1 | Partial-tap resistor, bridge | 2.2 kΩ ¼ W metal film | PRS value | <$1 |
| 1 | Treble bleed | as above | — | ~$1 |
| 1 | Output jack | Switchcraft #11 | — | ~$5 |
| — | Wire, foil, solder | as above | — | ~$30 |

**Subtotal: ~$80–100.** Cheapest and fastest of the three.

## Setup 3 — "Quiet"

Same as Setup 2, minus the two partial-tap resistors (no splits exist in this circuit).

**Subtotal: ~$78–98.**

## Pickups — all setups

| # | Item | Spec | ~Price |
|---|---|---|---|
| 2 | Custom-wound humbuckers | PAF class, 7.5–8.5 kΩ, 4-conductor + **separate** bare shield, **RWRP pair**, per-coil DCR matched within 10% | $200–500/pair |

Full text to send the winder is in [spec.md §6](spec.md#6-pickup-specification-for-the-winder).
The RWRP requirement and the separate bare shield are not optional — the first determines whether
positions 2 and 4 hum, the second determines whether the circuit works at all.

## Tools

| Item | Note |
|---|---|
| Soldering iron, 40 W+ with a chisel tip | A pencil tip will not heat a pot casing |
| Digital multimeter | Continuity + resistance. Mandatory for the bench tests. |
| Pole/magnet polarity tester | Or a compass — needed for the RWRP go/no-go check |
| Clip leads | For breadboarding the harness before installing it |
| Solder sucker / wick | You will use it |

## Not needed

- **Partial-tap resistors for Setup 1.** No valid insertion point — see
  [docs/pole-matrix.md](docs/pole-matrix.md).
- **A standard 2-pole 5-way blade.** It cannot express an HH map; both poles go to pickup selection.
  See [spec.md §3](spec.md#3-how-the-big-vendors-solve-this).
- **A "Dry Switch" network at the published values.** 330 kΩ ∥ 3300 pF corners at 146 Hz, not 3 kHz.
  If you want the low-cut, use ~470 kΩ ∥ 680 pF and measure it.
