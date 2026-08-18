# Three-row IRT-free maximum: construction and stop

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.

**Status.** The natural paper-shaped statement is \(F_3(n)=2n-2+(n\bmod 2)\)
for \(n\ge 4\). Lower bound is proved. Upper bound is **not** proved
(only checked for \(n\le 9\)). Not a paper. Stop. Not PROMISING for \(C(n)\).

Code: `fk.py`, `fk_struct.py`. Output: `out/F_k.json`.

---

## Object

\(F_3(n)\): max square-corner-free \(S\subseteq[n]^2\) on at most three rows.

## Theorem (lower bound)

For every \(n\ge 4\),

\[
F_3(n)\ge 2n-2+(n\bmod 2).
\]

- **Even \(n\):** two rows at distance \(n-1\), x-sets \(\{0,\ldots,n-2\}\).
  Size \(2n-2\) (`two_row.md`).
- **Odd \(n\):** rows \(0,1,n-1\); rows \(0\) and \(1\) take every even
  column; row \(n-1\) takes \(\{1,\ldots,n-2\}\). Size \(2\lceil n/2\rceil+(n-2)=2n-1\).
  Sq-free for every odd \(n=5,7,\ldots,31\) (`is_sq_free`). (The same point
  set is dirty for even \(n\): vertical \(w=(0,n-2)\) hits column \(0\).)

## Computer check, not a proof

| n | F_2 | F_3 | 2n-2+(n mod 2) | Q_SQ (OEIS A271906) |
|---|---|---|---|---|
| 4 | 6 | 6 | 6 | 6 |
| 5 | 8 | 9 | 9 | 9 |
| 6 | 10 | 10 | 10 | 11 |
| 7 | 12 | 13 | 13 | 14 |
| 8 | 14 | 14 | 14 | 17 |
| 9 | 16 | 17 | 17 | 20 |

Pairwise size bounds from \(F_2(n,d)\) are too weak to give \(2n-1\)
(they leave a slack of 2 on the maximising triple). Closing the upper bound
needs three-row IRTs. That case analysis did not close. Stop.

## What this is not

Not \(F_3(n)=2n-2+(n\bmod 2)\) as a theorem. Not \(Q_{\mathrm{SQ}}=O(n)\).
Not \(C(n)=O(n^{2-\varepsilon})\).
