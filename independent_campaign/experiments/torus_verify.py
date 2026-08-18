"""Independent verification of the g(7) = 8 witness and of the TENSOR LEMMA.

Written from scratch, sharing no code with torus_sq.py: the square-corner test here is
a naive triple loop over all ordered pairs with an explicit rotation, on the torus for
part 1 and over Z^2 for part 2.
"""
from itertools import product

W7 = [(0, 0), (0, 1), (0, 2), (0, 3), (1, 4), (3, 2), (4, 1), (6, 6)]


def torus_corners(T, q):
    """every (b,u,v) in T^3 with v = b + i*(u-b) on the torus, u != b"""
    S = set(T)
    out = []
    for b in S:
        for u in S:
            if u == b:
                continue
            wx, wy = (u[0] - b[0]) % q, (u[1] - b[1]) % q
            v = ((b[0] - wy) % q, (b[1] + wx) % q)
            if v in S:
                out.append((b, u, v))
    return out


def plane_corners(S):
    Ss = set(S)
    out = []
    for b in Ss:
        for u in Ss:
            if u == b:
                continue
            wx, wy = u[0] - b[0], u[1] - b[1]
            v = (b[0] - wy, b[1] + wx)
            if v in Ss:
                out.append((b, u, v))
    return out


def iso_free(pts):
    for b in pts:
        seen = set()
        for a in pts:
            if a == b:
                continue
            r = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r in seen:
                return False
            seen.add(r)
    return True


print("part 1 -- the g(7)=8 witness")
print(f"  |T| = {len(W7)}, distinct = {len(set(W7))}, all in [0,7)^2 = "
      f"{all(0 <= a < 7 and 0 <= b < 7 for a, b in W7)}")
print(f"  torus square corners = {len(torus_corners(W7, 7))}")
print(f"  a line {{(t,t)}} in (Z_7)^2 has {len(torus_corners([(t, t) for t in range(7)], 7))}"
      f" corners and only 7 points, so 8 > 7 is a strict improvement")
print(f"  as a subset of the PLANE [7]^2 it has "
      f"{len(plane_corners(W7))} square corners "
      f"(the torus condition is strictly stronger than the planar one)")
print(f"  isosceles-free? {iso_free(W7)}   (not required -- Q_SQ is a relaxation)")

print("\npart 2 -- tensor lemma, d = 2 and 3, from the q=7 witness")
for d in (2, 3):
    S = [tuple(sum(c[k] * 7 ** j for j, c in enumerate(combo)) for k in (0, 1))
         for combo in product(W7, repeat=d)]
    side = 7 ** d
    inbox = all(0 <= p[0] < side and 0 <= p[1] < side for p in S)
    nc = len(plane_corners(S))
    import math
    print(f"  d={d}: |S| = {len(S):5d} = 8^{d}, box side {side:4d} = 7^{d}, "
          f"in box = {inbox}, distinct = {len(set(S)) == len(S)}, "
          f"square corners = {nc}, exponent = {math.log(len(S))/math.log(side):.5f}")

print("\npart 3 -- planar consequence")
import math
print(f"  Q_SQ(7^d) >= 8^d, so Q_SQ(n) >= n^{math.log(8)/math.log(7):.5f} "
      f"along n = 7^d.")
print(f"  Q_SQ(7^7) = Q_SQ(823543) >= {8**7} = {8**7/7**7:.2f} * n")
