# NEXT_SESSION

**Run:** `long_horizon_run_20260811_183737/`  
**Read:** `RESEARCH_STATE.md`, `FAILED.md` (LH-F046+)

## Status

Incumbents 112/164. Parallel pattern/grow/rem3 jobs **harvested** — no +1.

## Harvest snapshot

- pattern-LNS best 133; grow-LNS best 134; grow_v3 best 135  
- rem3 s802 maximize recovered incumbent 164 (hash `8a84216d…`); s801 soft TIMEOUT 1800s

## Resume / live

1. Exact-LNS from S0 and from legal ~135 with larger destroy (see `SCRATCH/w3_lns_from_legal.py`).  
2. Do not reopen rem2 residual / killed Hamming / S0+1.  
3. Push after checkpoints.

## Standing order

`git add -A` → commit → `git push origin master` (no force). Ignore `.venv_solver`.
