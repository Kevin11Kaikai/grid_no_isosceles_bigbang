# Process Lessons

1. Prefer durable disk state (`RESEARCH_STATE.md`, experiment JSON) over chat memory.
2. Never equate scoped UNSAT or TIMEOUT with global optimality.
3. Gate1 consistency patch: n100 primary must be r=2; r=1 is negative-control only.
4. Score-based universes can be exhaustively killed quickly by CP-SAT; next universes need certificate/residual justification.
5. Agent C plateaus at Gate1 empirical min ΔV — soft search alone unlikely to break without new operators or exact residual repair.
6. Do not seed-grind; change model, universe definition, or mathematical reduction.
7. Never overwrite `results/certified/`; promote only into this run’s `CERTIFICATES/` then optionally export.
8. Point-pair / orbit scripts are bug-prone (H-006b lesson); assert occupancy before pair logic.
9. Keep n64 as cheap-kill sandbox; do not let it dominate vs n100.
10. Red-team: freeze Agent B report before declaring Gate2 fully closed.
11. **LH-2 critical:** All Wave2 Agent-C `n100_V3` elites are exactly `S0 ∪ {q}` (Hamming remove=0, add=1). Soft min-V at |S|=165 never left the single-insertion basin. Future fixed-card must **force** `|S0\\S|≥2` (or shuffle away from S0).
12. TIMEOUT at 90s can become INFEASIBLE with modest extra time (frame R2/r2: 90s TIMEOUT → 62s INFEAS on retry with 600s budget) — re-run borderline TIMEOUTs once before abandoning.
13. Standing order: commit+push meaningful checkpoints to `origin/master` (no force); do not stop research for polish.
14. **W3 orbit:** Enlarging Type0–6 defect universes (320/h18) still yields TIMEOUT≠INFEAS through 15–120min; cert_lb2 changes cut/round mix but not size>0. Prefer new encodings over more same-U wall-time.
15. Forced rem≥2 fixed-card swap LS leaves S0+1 basin but plateaus at V≈25–29; rem≥3 worse (V≈42).
16. **rem2 residual:** Soft cores ~150–160 often have addable < need (capacity fail ⇒ max≤164) or unique combos INFEAS. Full-involved strip + addable-restricted CP-SAT INFEAS in <1s on sampled seeds — do not grind that family.
