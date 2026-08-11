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
