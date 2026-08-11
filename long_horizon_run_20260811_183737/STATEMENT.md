# Frozen Problem Statement (Bootstrap — Immutable)

**Run:** `long_horizon_run_20260811_183737`  
**Frozen from:** `src/verification/oracle_verifier.py`, `src/verification_independent/independent_verifier.py`, Gate-0/1 audits, certified baselines.  
**Do not edit** unless a `CRITICAL_ISSUE.md` documents a verifier/definition contradiction.

## 1. Mathematical statement

For positive integer \(n\), let \([n]^2 = \{0,\ldots,n-1\}^2\).  
\(C(n)\) is the maximum cardinality of a subset \(S \subseteq [n]^2\) containing **no three distinct points** \(a,b,c\) with \(|a-b|=|b-c|\) (isosceles with apex \(b\)), under the distance convention below.  
Primary computational targets: improve certified lower bounds on \(C(64)\) and especially \(C(100)\).

## 2. Domain

Finite integer grid \([n]^2\). This run focuses on \(n=100\) (primary) and \(n=64\) (sandbox / method testbed).

## 3. Coordinate convention

`0_to_n_minus_1`: each point is a pair of Python `int` coordinates \((x,y)\) with \(0 \le x,y < n\).  
Bools and floats (even integer-valued) are rejected by both verifiers.

## 4. Isosceles definition (project semantics)

\(S\) is **illegal** iff there exist three **pairwise distinct** points \(a,b,c \in S\) such that  
\(\mathrm{sqdist}(a,b) = \mathrm{sqdist}(b,c)\).  
Equivalently: for every pivot \(b \in S\), the multiset of squared distances from \(b\) to all other points of \(S\) has **no repeated value**.

## 5. Squared distance

\(\mathrm{sqdist}((x_1,y_1),(x_2,y_2)) = (x_1-x_2)^2 + (y_1-y_2)^2\), computed with exact integer arithmetic (no floats for legality).

## 6. Distinct points

Duplicates are structurally invalid (rejected before legality). All forbidden triples use three distinct grid points.

## 7. Degenerate collinear cases

Collinear equally spaced triples (apex midpoint) are **forbidden**. Zero-area isosceles configurations count as illegal under the same apex-distance equality.

## 8. Equilateral inclusion

Any equilateral triangle has equal adjacent legs from each apex; such triples are illegal under the same definition (no special-case exclusion).

## 9. Valid / legal set

A candidate is **structurally valid** if coordinates and uniqueness pass, and **legal** if both independent verifiers report no forbidden triple (and equivalently \(V(S)=0\); see Gate 0).

Conflict metric (Gate 0 equivalence):
\[
V(S)=\sum_{b\in S}\sum_{d}\binom{m_{b,d}}{2},\quad
m_{b,d}=\#\{p\in S\setminus\{b\}:\mathrm{sqdist}(p,b)=d\}.
\]
\(V(S)=0 \iff S\) legal under project definition (fuzz-agreed in Gate 0).

## 10. Objective

Maximize \(|S|\) among legal subsets (equivalently raise certified lower bounds on \(C(n)\)).  
Search pilots may temporarily minimize \(V\) at fixed cardinality, but promotion requires \(V=0\) legality.

## 11. Construction vs proof

- **Construction / lower bound:** a concrete point set with dual-verified legality yields \(C(n)\ge |S|\).  
- **Restricted UNSAT / heuristic failure:** scoped only; **not** a global upper bound on \(C(n)\).  
- **Global structural exclusions** (e.g. Gate-1: every unselected cell on n=100 needs deletion LB ≥2 vs official baseline ⇒ global Hamming \(r=1\) shell around that baseline cannot reach 165) are labeled by evidence level and still do **not** alone prove \(C(100)\le 164\).

## 12. Incumbent constructions (certified)

| Grid | Size | Certificate | SHA-256 |
|---|---:|---|---|
| n=64 | 112 | `results/certified/n64_k112_baseline_official.json` | `47d42165b7804493a847e064494ef067e97bc8ac12121cd04ac19f23fee9c292` |
| n=100 | 164 | `results/certified/n100_k164_baseline_official.json` | `8a84216d28f5afbbbd6b06301b159eab1b57c85bb814d78dd708da2be65cbdc1` |

Both: `status=DUAL_VERIFIED`, `verifier_A_pass=true`, `verifier_B_pass=true`.  
No stronger dual-certified construction exists in-repo at bootstrap.

## 13. Bound evidence levels (claim discipline)

| Level | Meaning | Allowed claim |
|---|---|---|
| `HEURISTIC` | Search did not find | No UB/LB promotion |
| `SCOPED_INFEASIBLE` | Exact solver UNSAT under explicit universe/r/symmetry/seed | Scoped wording only |
| `GLOBAL_SHELL_EXCLUSION` | Sound argument excluding a whole shell class around a fixed S0 | Structural; not \(C(n)\le k\) alone |
| `GLOBAL_RIGOROUS_LOWER_BOUND` (deletion) | Sound VC LB on blockers for all unselected cells | Used for r-policy (n100: ≥2) |
| `DUAL_VERIFIED_CONSTRUCTION` | Two independent verifiers PASS + hash + bundle | New lower bound \(C(n)\ge |S|\) |

## 14. Dual verification requirement for promotion

No new lower bound without: frozen points, Verifier A + Verifier B PASS, \(V=0\), canonical hash, certificate bundle under this run’s `CERTIFICATES/`, and independent re-check under `VERIFICATION/`. Never overwrite sealed historical artifacts under `results/certified/`.

## 15. Primary policy freeze (Gate 1)

- **n=100 primary:** Hamming exchange radius **r=2** (\(|S_0\setminus S|=2\), \(|S\setminus S_0|=3\), target 165).  
  Universe lineage starts at `U_small_r2` (76 vars, hash `a100c8b6…0e88`); Wave-2 scored that and several halos `INFEASIBLE_SCOPED` — new Rem/Add constructions must be justified.  
- **n=100 r=1:** negative-control / encoding sanity only (global r=1 shell excluded by blocker LB).  
- **n=64:** exact min deletion = 1 for easiest cells; r=1 valid as sandbox; must not dominate budget vs n=100.
