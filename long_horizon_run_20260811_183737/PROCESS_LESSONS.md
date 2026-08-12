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
14. **W3 orbit:** Enlarging Type0–6 defect universes (320/h18) still yields TIMEOUT≠INFEAS through 15–60min; cert_lb2 defect ranking changes cut/round mix but not size>0. Prefer ≥2h on one promising U or new encodings over more 30min type sweeps.
15. Forced rem≥2 fixed-card swap LS leaves S0+1 basin but plateaus at V≈28–29 — not a substitute for exact residual repair.
