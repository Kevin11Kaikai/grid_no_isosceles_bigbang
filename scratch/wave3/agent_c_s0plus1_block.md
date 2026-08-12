# BLOCK — Agent C S0+1 soft seed grinding

**Status:** ACTIVE BLOCK (Wave3, post-Gate2)  
**Date:** 2026-08-12

## Reason

Wave2 Agent C + LH elite analysis: all n100 V=3 elites are exactly **S0 ∪ {q}** (Hamming remove=0). Soft |S|=165 search plateaued at V=3 matching Gate1 min direct-insertion ΔV and never left that basin. Further seeds on the same operators are seed grinding.

## Forbidden

- More fixed-cardinality soft campaigns initialized as baseline+low-blocker / Gate1-low-ΔV / orbit-informed with the Wave2 move set aimed at grinding V→0 from S0∪{q}.
- Treating V=3/V=2 plateaus as impossibility proofs.

## Allowed only if reformulated

- Fixed-card / soft search that **forces remove≥2** from S0, or uses nonlocal free variables / a new neighborhood formulation.
- Exact residual repair under free-sets **not** already killed in `FAILED.md` (LH-F003 etc.).

## Evidence refs

- `scratch/agent_c/agent_c_wave2_report.md`
- `long_horizon_run_20260811_183737/FAILED.md` IMP-F006
- `scratch/wave2/gate2_decision.md` §5–6
