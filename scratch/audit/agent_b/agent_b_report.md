# Audit Agent B — Orbit / Parity / Reachability (Gate 1)

- **git HEAD**: `148808f422cba7e8ca232ebb4710b84782086342`
- **Baseline n=64**: size 112, sha256 `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` (Gate0 match=True)
- **Baseline n=100**: size 164, sha256 `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` (Gate0 match=True)
- **Targets**: 113 (n=64), 165 (n=100). Statuses use FULL-orbit subset-sum only.
- **No search performed.** No legality solvers. No `src/search` modules created.

## B1 — Recovered notebook symmetries

Source: `data/external/subsets_of_the_grid_with_no_isosceles_triangles.ipynb` (`get_symmetric_partners`).

Offsets (exact):

```
offsets = [
  (n-1, n-1),  # type 0
  (n-2, n-2),  # type 1
  (n, n),      # type 2
  (n, n-1),    # type 3
  (n-2, n-1),  # type 4
  (n-1, n),    # type 5
  (n-1, n-2),  # type 6
]
sym_x, sym_y = offset_x - x, offset_y - y
partners = {(sym_x,y), (x,sym_y), (sym_x,sym_y)} ∩ grid \ {p}
```

Partner transform is the Klein four-group of axis reflections with `c ↦ offset - c` (i.e. reflection across `A = offset/2`), **restricted** by dropping out-of-grid images. Mapping semantics are clear from code (not `mapping_semantics_blocked`).

Repo `src/search/symmetry_guided.py` differs: it only uses central 180° `(n-1-x, n-1-y)` pairs (Type 0’s `rxy`), not the seven axis-offset types.

### Per-type group-action / orbit notes (both n even)

| Type | Offset (n=64) | True G-action on full grid? | OOG pts (n64) | FULL size multiset (n64) | Fixed FULL orbits |
|---:|---|---|---:|---|---|
| 0 | `[63, 63]` | True | 0 | {'4': 1024} | components=0, FULL size-1=0 |
| 1 | `[62, 62]` | False | 127 | {'1': 1, '2': 62, '4': 961} | components=4, FULL size-1=1 |
| 2 | `[64, 64]` | False | 127 | {'1': 1, '2': 62, '4': 961} | components=4, FULL size-1=1 |
| 3 | `[64, 63]` | False | 64 | {'2': 32, '4': 992} | components=0, FULL size-1=0 |
| 4 | `[62, 63]` | False | 64 | {'2': 32, '4': 992} | components=0, FULL size-1=0 |
| 5 | `[63, 64]` | False | 64 | {'2': 32, '4': 992} | components=0, FULL size-1=0 |
| 6 | `[63, 62]` | False | 64 | {'2': 32, '4': 992} | components=0, FULL size-1=0 |

Only **Type 0** (`offset=(n-1,n-1)`) is a true Klein-four group action on the entire `[0,n)²` grid (0 out-of-grid formal images). **Type 1** (`n-2,n-2`) reflects the far boundary `n-1 ↦ -1` (OOG). **Type 2** (`n,n`) reflects `0 ↦ n` (OOG). Mixed types 3–6 each have one OOG-producing axis. Truncated/boundary components are excluded from pure FULL-orbit cardinality. Types **1 and 2** each admit exactly one FULL size-1 fixed orbit at the integer axis intersection `(⌊offset_x/2⌋, ⌊offset_y/2⌋)` — i.e. `(n/2-1,n/2-1)` for type 1 and `(n/2,n/2)` for type 2 — which is what makes odd targets cardinality-reachable.

## B2 — Baseline orbit completeness

### n=64 / 112

| Type | Fully present (any) | Fully present FULL-type | Partial | Empty | FULL sym core (pts) | Deletes (partial) | Adds to complete |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 27 | 27 | 2 | 995 | 108 | 4 | 4 |
| 1 | 1 | 0 | 101 | 987 | 0 | 110 | 278 |
| 2 | 1 | 0 | 99 | 989 | 0 | 110 | 270 |
| 3 | 6 | 4 | 46 | 1004 | 16 | 92 | 92 |
| 4 | 6 | 4 | 46 | 1004 | 16 | 92 | 92 |
| 5 | 3 | 0 | 54 | 999 | 0 | 106 | 110 |
| 6 | 3 | 0 | 54 | 999 | 0 | 106 | 110 |

### n=100 / 164

| Type | Fully present (any) | Fully present FULL-type | Partial | Empty | FULL sym core (pts) | Deletes (partial) | Adds to complete |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 | 41 | 41 | 0 | 2459 | 164 | 0 | 0 |
| 1 | 2 | 0 | 130 | 2469 | 0 | 160 | 336 |
| 2 | 2 | 0 | 130 | 2469 | 0 | 160 | 336 |
| 3 | 10 | 7 | 65 | 2475 | 28 | 130 | 130 |
| 4 | 10 | 7 | 65 | 2475 | 28 | 130 | 130 |
| 5 | 11 | 6 | 65 | 2474 | 24 | 130 | 130 |
| 6 | 11 | 6 | 65 | 2474 | 24 | 130 | 130 |

Notes: n=100 Type 0 has **0 partial orbits** and FULL core 164/164 (exact central reflection symmetry, consistent with H-001). n=64 Type 0 has FULL core 108/112 with 2 partial orbits (4 pts present / 4 missing). Structural distance is descriptive only (not a construction search).

## B3 — Cardinality reachability (FULL orbits → subset-sum)

| Type | n=64 → 113 | n=100 → 165 | Defects for cardinality? | Phase 2 |
|---:|---|---|---|---|
| 0 | unreachable | unreachable | 64:True/100:True | defects mandatory (both targets) |
| 1 | reachable (legality open) | reachable (legality open) | 64:False/100:False | compare pure-orbit vs orbit+defect |
| 2 | reachable (legality open) | reachable (legality open) | 64:False/100:False | compare pure-orbit vs orbit+defect |
| 3 | unreachable | unreachable | 64:True/100:True | defects mandatory (both targets) |
| 4 | unreachable | unreachable | 64:True/100:True | defects mandatory (both targets) |
| 5 | unreachable | unreachable | 64:True/100:True | defects mandatory (both targets) |
| 6 | unreachable | unreachable | 64:True/100:True | defects mandatory (both targets) |

### Defect / Phase-2 classification (all 7 types)

- **Require defects for cardinality (both 113 and 165 unreachable)**: types [0, 3, 4, 5, 6]
- **Compare pure-orbit vs orbit+defect** (cardinality reachable; legality open): types [1, 2]
- **mapping_semantics_blocked**: types ∅

Mathematical mandatory-defect theorem applies **only** to `cardinality_unreachable` types. Reachable types must still be searched both ways in Phase 2; cardinality ≠ legality.

### Unreachability proofs (where applicable)

**n=64 target 113**

- Type 0: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 1: reachable via FULL-orbit subset-sum (max_sum=3969); legality open.
- Type 2: reachable via FULL-orbit subset-sum (max_sum=3969); legality open.
- Type 3: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 4: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 5: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 6: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.

**n=100 target 165**

- Type 0: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 1: reachable via FULL-orbit subset-sum (max_sum=9801); legality open.
- Type 2: reachable via FULL-orbit subset-sum (max_sum=9801); legality open.
- Type 3: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 4: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 5: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.
- Type 6: All FULL orbit sizes are even, target is odd ⇒ impossible by parity.

## Files written

- `scratch/audit/agent_b/orbit_parity_reachability.json`
- `scratch/audit/agent_b/orbit_completeness_n64.json`
- `scratch/audit/agent_b/orbit_completeness_n100.json`
- `scratch/audit/agent_b/agent_b_report.md`
- `scratch/audit/agent_b/scripts/orbit_audit.py`
