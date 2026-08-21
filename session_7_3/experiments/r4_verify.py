# -*- coding: utf-8 -*-
"""Round 4, probe 4.2 -- adversarial verification of the doubling mechanism.

Two independent checks:
 (1) the mod-4 separation claim, tested exhaustively on raw lattice vectors;
 (2) the doubling T = 2S u (2S+(a,b)) built from an (H)-satisfying S, checked
     isosceles-free by a NAIVE triple loop that knows nothing about parity.
Also verifies the triangular-number restatement of (H).
"""
import random, sys
from r4_double import greedy, isofree_bruteforce

# --- (1) the mod-4 / mod-8 separation, exhaustively -------------------------
bad = 0
for dx in range(-40, 41):
    for dy in range(-40, 41):
        d = dx*dx + dy*dy
        if dx % 2 == 0 and dy % 2 == 0:
            if d % 4 != 0: bad += 1
        elif dx % 2 != 0 and dy % 2 != 0:
            if d % 8 != 2: bad += 1
print("(1) separation  (even,even)->0 mod 4 and (odd,odd)->2 mod 8 :"
      "  violations over 81x81 vectors =", bad)

# --- triangular-number restatement -----------------------------------------
bad2 = 0
for wx in range(-30, 31):
    for wy in range(-30, 31):
        T = lambda w: w*(w+1)//2
        lhs = (2*wx+1)**2 + (2*wy+1)**2
        if lhs != 8*(T(wx)+T(wy)) + 2: bad2 += 1
print("(2) restatement (2w+1)^2+(2z+1)^2 = 8(T(w)+T(z))+2 :  violations =", bad2)

# --- (3) end-to-end: build S with (H), double it, verify naively -----------
print()
print("(3) end-to-end doubling check")
print("   n  |S|  (a,b)      |T|  T in [2n]^2?  T isosceles-free (naive)?")
allok = True
for n in (5, 6, 7, 8, 9, 10, 11, 12, 13, 16):
    best = None
    for a, b in ((1,1), (1,-1), (3,1), (1,3), (3,3), (5,-3), (9,11), (11,-11)):
        for s in range(120):
            S = greedy(n, (a, b), s)
            if best is None or len(S) > len(best[0]): best = (S, (a, b))
    S, (a, b) = best
    T = [(2*x, 2*y) for (x, y) in S] + [(2*x+a, 2*y+b) for (x, y) in S]
    lo = min(min(p) for p in T); hi = max(max(p) for p in T)
    span = hi - lo + 1
    inbox = span <= 2*n
    ok, wit = isofree_bruteforce(T)
    allok = allok and ok and (len(T) == 2*len(S))
    print("  %3d %4d  %-9s %4d   span=%-4d %-6s  %s"
          % (n, len(S), str((a,b)), len(T), span, str(inbox), "YES" if ok else "NO %s" % (wit,)))
    sys.stdout.flush()
print()
print("ALL DOUBLINGS VALID:", allok)
