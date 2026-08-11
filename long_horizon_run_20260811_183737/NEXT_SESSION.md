# NEXT_SESSION (≤1 page)

**Run dir:** `long_horizon_run_20260811_183737/`  
**Read first:** `RESEARCH_STATE.md`, `FAILED.md`, `REGISTRY.md`.

## Resume files

- Experiments: `EXPERIMENTS/LH1_blocker_pair/`, `EXPERIMENTS/LH1_v3_residual/`, `EXPERIMENTS/LH1_n64_sandbox/`
- Next scripts: `SCRATCH/u_fullrem_lowlb_r2.py`, then single-q large-Add shells
- Incumbent unchanged: `INCUMBENT.json`

## Next 3 actions

1. Finish / interpret `U_fullrem_LBle4_r2` Hamming CP-SAT (n100, r=2).
2. Single exact-2 q: Rem=its size-2 covers, Add=all LB≤5 cells, search r=2.
3. Short Agent-B orbit smoke (new seed/type); no TIMEOUT grind.

## Standing order

After each meaningful checkpoint: `git add -A` → commit → `git push origin master` (no force). Continue research; do not Hard Stop on Wave complete.
