# Sealed-S0 Mechanism Tournament

**Started:** 2026-08-14  
**Parent run:** `long_horizon_run_20260811_183737/`

## Isolation (discovery agents)

Blind constructors **must not**:
- import `data.baselines.official_raw` / certified JSON coordinates
- Hamming-exchange around official S0
- read Wave2 U_ids, Gate1 easiest-q lists, or S0 blocker covers

They **may** know only scalar thresholds: beat **113** on n=64, **165** on n=100.

They **must** use existing verifiers:
- `src/verification/oracle_verifier.py`
- `src/verification_independent/independent_verifier.py`

## Orchestrator (not sealed)

Keeps FAILED/PROVED: official S0 frozen-core r=1/r=2 is **deprioritized**, not a discovery seed.
Unsealed side-basin: dual-verified 147 LNS may continue with **limited** budget (not the tournament's only worldview).

## Status vocabulary

`EXPLORING` / `PROMISING` / `BLOCKED` / `FALSIFIED` / `DEPRIORITIZED` / `VERIFIED` / `CHAMPION`

FALSIFIED only via counterexample, impossibility, or exhaustive finite class.
Failure to beat the threshold ≠ optimality.

## Mission

Find a dual-verified legal S with |S|≥113 (n=64) or |S|≥165 (n=100) generated **without** official S0 coordinates.

## Results (2026-08-14)

| Wave | n | Best | Mech | Beat | Hash prefix |
|---|---:|---:|---|---|---|
| 1 | 64 | 84 | T-F | no | `4c0d83a51ef4` |
| 2 | 64 | 90 | T-F | no | `de1148b1f4a9` |
| 2 | 100 | 137 | T-F | no | `971f1240933f` |

No `CANDIDATES/` promotion. Sealed 137 < unsealed 147 < incumbent 164. Next sealed branch: longer T-K keep55-style cores (cap~789 worked; keep40 free=2260 did not).
