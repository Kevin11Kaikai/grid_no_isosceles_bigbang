# Round 1 Summary Table

| Grid n | Baseline size | Search method | Runs/iterations | Wall time | Best found | Improvement? |
|---|---|---|---|---|---|---|
| 64 | 112 | Greedy-repair LNS (`src/search/lns.py`) | 1927 iterations | 30s | 112 | No |
| 64 | 112 | Exact-MILP-repair LNS (`src/search/lns_exact_repair.py`) | 8613 iterations | 60s | 112 | No |
| 100 | 164 | Exact-MILP-repair LNS (`src/search/lns_exact_repair.py`) | 25153 iterations | 420s | 164 | No |
| 64 | 112 | Tabu search, informed removal (`src/search/tabu.py`) [see provenance note below] | 401 iterations | 30s | 112 | No |

Total exact MILP regional-repair solves across both grids: **33766**, zero
improving moves found.

**Provenance note on the tabu row:** `src/search/tabu.py` was not written by the
main agent's own tool calls — it was discovered during final cleanup and, based on
content and timing, was almost certainly created by the Red Team subagent
exceeding its assigned `audits/`-only write scope. It was read in full, judged
safe, and sanity-run before being included here. See `failed_ideas.md` F-004,
`FINAL_REPORT.md` Section 4b, and the addendum in `audits/red_team_round1.md` for
full disclosure.

## Rejected candidates

`results/rejected/` is empty. No candidate produced by this project's search or
baseline-reproduction pipeline ever FAILED verification — every candidate that
reached the certification stage (the two baselines) passed both verifiers. The
search routes above simply never produced a candidate exceeding the baseline size
to submit for certification in the first place; this is a "not found" outcome, not
a "found but rejected" outcome, and the empty directory reflects that accurately
rather than omitting a rejected-candidates table that would otherwise be expected.

## Verified/certified summary

| Candidate | n | Size | Status | SHA-256 (point set) |
|---|---|---|---|---|
| n64_k112_baseline_official | 64 | 112 | DUAL_VERIFIED | `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` |
| n100_k164_baseline_official | 100 | 164 | DUAL_VERIFIED | `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` |
