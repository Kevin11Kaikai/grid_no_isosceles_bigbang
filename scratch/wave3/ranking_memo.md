# Wave3 Ranking Memo

**Date:** 2026-08-12  
**Gate2:** PASS / CLOSED (`4ddf9ab`); `WAVE3_READY`  
**Incumbents:** \(C(64)\ge 112\), \(C(100)\ge 164\) (no new dual-certified +1)

## Ranking criteria

Score routes by: (1) open TIMEOUT information gain, (2) scoped progress vs killed U_ids, (3) diversity vs Wave2 score-shells / S0∪{q} soft basin, (4) exactness / certificate grounding. Prefer microproblems over seed grinding.

## Top routes funded now

### R1 — PRIMARY: Enlarged Type0 orbit-defect (TIMEOUT-open)

| Item | Choice |
|---|---|
| Why | Wave2 + LH4 Type0 defect longs consistently **TIMEOUT size=0**, never INFEAS; pure T1/T2 already scoped-killed. Highest remaining open information. |
| Universe | `orb_t0_defect_*_def220_h14` (distinct from Wave2 halo=8 / max_extra=100) |
| Live job | n100 Type0 defect s401, 45 min, dmax=12 (in flight) |
| Next if TIMEOUT | Further enlarge: `max_extra/defect≥320`, `halo≥18`, and/or `agent_c_universe=U_large`, longer wall; optional n64 Type0 enlarge sandbox |
| Claim discipline | TIMEOUT ≠ INFEASIBLE; scoped UNSAT ≠ global UB |

### R2 — SECONDARY: Certificate-driven Hamming Rem/Add (outside killed U_ids)

| Item | Choice |
|---|---|
| Why | Wave2 score `U_*` + several LH fullrem/low-LB Add pools are **DEAD** (`FAILED.md` IMP-F004, LH-F004…); Gate2 mandates Rem/Add rebuilt from certificates / residuals. |
| Cheap-kill first | Short CP-SAT (≤120s) on new U_ids before long budget |
| Pilot U_ids (new) | (a) `U_cert_involved_e16_Add_e56_r2` — Rem=union involved baselines of LB≤2 qs; Add=LB≤3 qs; **r=2**. (b) `U_certfreq_top48_Add_LBle5_r2` — Rem=top-48 q-weighted cert-frequency verts; Add=LB≤5; **r=2**. |
| Explicitly excluded | Wave2 `U_small` / `U_small_r2` / score-halo / prior fullrem-LBle4 shells |

## Explicitly KILLED / blocked this Wave

| Route | Action |
|---|---|
| Agent C S0+1 soft seed grinding | **BLOCKED.** All Wave2 n100 V=3 elites = S0∪{q} (Hamming remove=0). Do not spend primary budget on more baseline+1 fixed-card soft seeds. |
| Fixed-card if reused | Require **remove≥2** or nonlocal free vars / new formulation; residual exact repair only under new free-sets. |
| FunSearch / Phase-5 | **HOLD.** No new structure justifying it after G2; revisit only if R1/R2 produce new basin structure or soft metrics move after focused exact runs. |
| Reopening FAILED entries | Forbidden without new reason / new U_id / new formulation. |

## Budget split (Wave3 focus)

- ~55% R1 orbit Type0 enlarge / long TIMEOUT
- ~35% R2 cert Hamming cheap-kill → fund only survivors
- ~10% critic / dual-verify / ledger (always on)
- 0% FunSearch; 0% C S0+1 soft grind

## Success / stop conditions

- Promote only after dual verifiers + certificate bundle; do not touch `claim_registry` / `results/certified` without that.
- Continue Explore→CheapKill→Compute→Verify until certified +1 or hard stop; update `NEXT_SESSION.md` on handoff.
