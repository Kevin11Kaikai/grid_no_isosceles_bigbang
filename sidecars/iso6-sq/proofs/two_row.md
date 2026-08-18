# Theorem: two-row square-corner-free maximum

This file lives in `d:\others\iso6-sq\proofs\`. It is **not** an iso6 proof.
Do not copy into `iso6/docs/`, `iso6/proofs/`, or `iso6/routes/`.

**This is not** `Q_SQ(n)=O(n)` and **not** `C(n)=O(n^{2-\varepsilon})`.
A square-corner-free set may occupy every row (Gaussian peeling does).

Code: `two_row.py`. Output: `out/two_row.json`.

---

## Theorem

Let \(F_2(n)\) be the maximum size of a square-corner-free \(S\subseteq[n]^2\)
whose points lie on at most two rows. For every \(n\ge 2\),

\[
F_2(n)=2n-2.
\]

The same bound holds for at most two columns (rotate \(90^\circ\)).

**Equality.** Rows \(0\) and \(n-1\), both with x-set \(\{0,\ldots,n-2\}\)
(or both \(\{1,\ldots,n-1\}\)). Size \(2n-2\). Checked sq-free for
\(n=3,4,5,8,16,32,48,64\).

---

## Classification

Write the two rows as \(y\) and \(y+d\) with \(1\le d\le n-1\), and x-sets
\(A,B\subseteq\{0,\ldots,n-1\}\). Let \(I=A\cap B\) and \(U=A\cup B\).
A single row is square-corner-free, so any square-corner in \(S\) uses both
rows (distribution \(2+1\)).

The third point of a pair in \(S\) that leaves the two rows is not in \(S\).
The vectors \(w\) that keep all three points on the two rows are:

1. **Vertical.** Apex \((x,y)\), partner \((x,y+d)\), so \(x\in I\). Then
   \(R_\pm(0,d)=(\pm d,0)\) forbids \((x\pm d,y)\). Apex on the top row
   likewise forbids \((x\pm d,y+d)\). Hence
   \((I\pm d)\cap U=\emptyset\). In particular \(I\) has no two elements
   at distance \(d\).
2. **Horizontal of length \(d\).** Apex \((x,y)\), partner \((x+d,y)\),
   third \((x,y+d)\): this is \(x\in I\) and \(x+d\in A\), already forbidden
   by (1).
3. **Diagonal.** Apex \((x,y)\in A\), partner \((x+p,y+d)\in B\),
   \(w=(p,d)\). Then \(R_+(w)=(-d,p)\) has y-offset \(p\), which lands on
   the two rows iff \(p\in\{0,d\}\). The case \(p=0\) is vertical. The case
   \(p=d\) is \(x\in A\) and \(\{x-d,x+d\}\subseteq B\). The other
   orientation \(p=-d\) is the same condition. Apex on top: \(x\in B\) and
   \(\{x-d,x+d\}\subseteq A\).

No other \(p\) works. Machine check: this predicate agrees with `is_sq_free`
on every pair of subsets for \(n=2,\ldots,8\) (0 mismatches;
`n_combo_ok=n_is_sq_free` in `out/two_row.json`).

---

## Upper bound

The sets \(A\setminus I\), \(B\setminus I\), and \(I\) are pairwise disjoint
subsets of \(\{0,\ldots,n-1\}\), so

\[
|S|=|A|+|B|=|A\setminus I|+|B\setminus I|+2|I|\le n-|I|+2|I|=n+|I|.
\]

- If \(|I|=n\), then \(A=B=[n]\): two full rows, which contain a
  square-corner (lemma in `upper_bound.md`: \((d,y)\), \((d,y+d)\), \((0,y)\)).
- If \(|I|\le n-2\), then \(|S|\le n+(n-2)=2n-2\).
- If \(|I|=n-1\), write \(I=[n]\setminus\{m\}\). The graph on \([n]\) with
  edges \(\{i,i+d\}\) has \(n-d\ge 1\) edges. Because \(I\) has no two
  elements at distance \(d\), the omitted column \(m\) meets every such
  edge, so \(m\) is an endpoint of some pair \(\{t,t+d\}\). The other
  endpoint lies in \(I\), hence \(m\in(I\pm d)\cap[n]\). Rule (1) forces
  that column out of \(U\), so \(m\notin U\), \(|U|\le n-1\), and
  \(|S|=|U|+|I|\le 2n-2\).

---

## Enumeration

| n | F_2 | 2n-2 |
|---|---|---|
| 2 | 2 | 2 |
| 3 | 4 | 4 |
| 4 | 6 | 6 |
| 5 | 8 | 8 |
| 6 | 10 | 10 |
| 7 | 12 | 12 |
| 8 | 14 | 14 |

---

## Theorem 2 (consecutive rows)

Let \(F_2(n,1)\) be the maximum on two rows at distance \(1\). For \(n\ge 2\),

\[
F_2(n,1)=n+(n\bmod 2).
\]

**Equality.** Both rows use the even columns: size \(2\lceil n/2\rceil=n+(n\bmod 2)\).

**Proof.** The two-row classification applies with \(d=1\). Let \(I=A\cap B\),
\(U=A\cup B\), \(J=((I+1)\cup(I-1))\cap[n]\). Vertical forbids \(J\cap U=\emptyset\),
and \(I\) has no two consecutive elements. Then \(|S|=|U|+|I|\le n-|J|+|I|\).

Write \(p\) for the number of pairs in \(I\) at distance \(2\). The two
one-step shifts overlap once per such pair, and miss the grid once at each
endpoint of \([n]\) that lies in \(I\), so

\[
|J|=2|I|-1_{0\in I}-1_{n-1\in I}-p,
\]
hence \(|I|-|J|=-|I|+1_{0\in I}+1_{n-1\in I}+p\). An isolated set on a line
has \(p\le|I|-1\), with equality iff \(I\) lies in a single residue class
modulo \(2\). Thus \(|I|-|J|\le 1\), and equality requires both endpoints
in \(I\) and one residue class, so \(0\) and \(n-1\) have the same parity:
\(n\) odd. If \(n\) is even then \(|I|-|J|\le 0\). Therefore
\(|S|\le n+(n\bmod 2)\).

---

## What this is not

Claude’s table has \(Q_{\mathrm{SQ}}(5)=9>8\) and \(Q_{\mathrm{SQ}}(6)=11>10\):
those extra points use a third row. Peeling uses many rows. This theorem
does not bound \(Q_{\mathrm{SQ}}(n)\) or \(C(n)\).
