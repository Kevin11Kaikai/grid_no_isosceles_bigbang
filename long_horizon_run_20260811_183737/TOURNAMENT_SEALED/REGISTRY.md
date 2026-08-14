# Approach Registry — sealed tournament

Thresholds only: n64≥113, n100≥165. No S0 coordinates in these routes.

| ID | Mechanism | Status | Best n64 | Best n100 | Notes |
|---|---|---|---:|---:|---|
| T-A | Lookahead greedy | BLOCKED (wave1) | 70 | — | Dual-OK; far below 113 |
| T-B | Algebraic graphs + fill | BLOCKED (wave1) | 75 | — | Dual-OK |
| T-C | Scale-lift from small n | BLOCKED (wave1) | 74 | — | Dual-OK |
| T-D | Two-per-row / col templates | BLOCKED (wave1) | 77 | — | Dual-OK; best wave1 seed |
| T-E | Beam grow | BLOCKED (wave1) | 69 | — | Dual-OK |
| T-F | LNS from best sealed seed | BLOCKED (this budget) | 90 | 137 | Wave2: n64 84→90; n100 135→137 |
| T-G | Greedy multistart (from scratch) | BLOCKED (wave2) | 80 | 118 | Dual-OK |
| T-H | Coupled 180° symmetric build | BLOCKED (wave2) | 78 | 116 | Dual-OK; no S0 coords |
| T-I | Knight / quad / stair / lattice grow | BLOCKED (wave2) | 78 | 120 | Dual-OK |
| T-J | Tabu from best sealed | BLOCKED (wave2) | 84 | 130 | n100 120→130 |
| T-K | Medium-core + generic rot180 blacklist max | PROMISING (short) | 80 | 135 | n100 keep55: 70+719 cap=789 → 135; keep40 free=2260 unusable |
| T-L | CP-SAT lazy maximize warm-start | BLOCKED (wave2) | 84 | 135 | No improve on warm start |
| U-147 | Asymm-west 147 (UNSEALED) | PROMISING | — | 147 | Orchestrator-only; still larger than sealed 137 |

Official S0 Hamming r=1/r=2: **DEPRIORITIZED** (see PROVED.md §6–9). Not in this tournament.
