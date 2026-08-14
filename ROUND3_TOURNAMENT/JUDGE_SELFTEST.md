# Judge self-test — `ROUND3_TOURNAMENT/judge.py`

Protocol Section 9 requires that the adjudicator itself be attacked before it is
trusted. Six adversarial fixtures were generated (script:
`scratchpad/mk_judge_fixtures.py`, fixtures written outside the repo) and run
through the judge.

## Two defects found in the harness (both fixed)

1. **`bool()` on a tuple return — severity HIGH.**
   `independent_verifier.verify_independent(points, n)` returns
   `(is_legal, witness)`, not a bare bool. The harness coerced the tuple with
   `bool(...)`, which is **always True** for a 2-tuple. Effect: the independent
   verifier was reporting PASS unconditionally, so a candidate could be
   rubber-stamped `DUAL_VERIFIED` while actually illegal. Caught by fixture f2
   (three collinear equally-spaced points), which surfaced as
   `VERIFIER_DISAGREEMENT` — the oracle said illegal, the mis-read independent
   said legal. Fixed by unpacking explicitly and recording the witness.

   This is precisely the failure mode the judge exists to prevent, and it was in
   the judge. Note the verifiers themselves were correct throughout; the defect
   was entirely in the calling harness.

2. **Substring collision on status check — severity LOW.**
   The status-forgery test used `"VERIF" in status`, which matches
   `"UNVERIFIED"`. Effect: honest `UNVERIFIED` candidates were falsely flagged as
   claiming verification. Fixed to require `"VERIFIED" in s and "UNVERIFIED" not
   in s`.

## Post-fix results — all six fixtures adjudicate correctly

| Fixture | Attack | Verdict | Caught |
|---|---|---|---|
| f1 | none (genuinely legal, n=8, \|S\|=9) | `DUAL_VERIFIED` | — (correctly clean) |
| f2 | illegal collinear midpoint + status forged to `DUAL_VERIFIED` | `ILLEGAL` | legality + status forgery |
| f3 | `size` field forged to 999 vs 2 real points | `MALFORMED` | rejected at load |
| f4 | claims n=4, contains (9,9) | `ILLEGAL` | out-of-range + implied n≥10 |
| f5 | duplicate point inflating size | `ILLEGAL` | duplicate detected |
| f6 | legal set, stored sha256 replaced with `deadbeef…` | `LEGAL_BUT_FLAGGED` | sha mismatch |

Exit code 1 (flags present), as designed.

## Checks the judge runs that a producing route has no incentive to run

- forged `size` field · duplicate points · out-of-range coordinates · claimed *n*
  vs *n* implied by coordinates · stored sha vs recomputed sha · self-reported
  status vs re-derived verdict
- **three** legality paths where affordable: oracle per-pivot, oracle
  brute-force all-triples (O(k³), used for |S| ≤ 60), and the independent numpy
  argsort verifier. Any disagreement between paths is reported as
  `VERIFIER_DISAGREEMENT` and treated as outranking every search result, since a
  verification-pipeline defect invalidates all downstream claims.
