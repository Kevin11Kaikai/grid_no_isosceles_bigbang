"""Lower bounds on g(q) for larger q -- the live falsification instrument.

The square-corner route dies iff some construction reaches n^{2-o(1)}, i.e. iff
log g(q)/log q -> 2.  A LOWER bound on g(q) is therefore what could kill it, so
heuristic search is the right tool and the asymmetry runs in our favour: if search
cannot push the exponent up, that is evidence the route survives; if it can, the route
is dead and we will know.

Addability test (complete).  A violation is (b,u,v), u != b, v = i*u + (1-i)*b.  A new
point p can occupy any of the three roles, so three O(|S|) scans suffice:
    p = b : some u in S with i*u + (1-i)*p in S
    p = u : some b in S with i*p + (1-i)*b in S
    p = v : some b in S with i^{-1}(p - (1-i)b) in S
Every set produced is then re-checked against the complete O(|S|^2) definition.
"""
import math
import random
import sys


def make_ops(q):
    """return functions for  i*z,  (1-i)*z,  i^{-1}*z  on (Z_q)^2"""
    def rot(z):                      # i*z
        return ((-z[1]) % q, z[0] % q)

    def omi(z):                      # (1-i)*z = (z1+z2, z2-z1)
        return ((z[0] + z[1]) % q, (z[1] - z[0]) % q)

    def irot(z):                     # i^{-1} z = -i z
        return (z[1] % q, (-z[0]) % q)
    return rot, omi, irot


def greedy(q, restarts, rng):
    rot, omi, irot = make_ops(q)
    cells = [(x, y) for x in range(q) for y in range(q)]
    best = []
    for _ in range(restarts):
        rng.shuffle(cells)
        S = set()
        for p in cells:
            ip, op = rot(p), omi(p)
            ok = True
            for s in S:
                # p as apex b:  v = i*s + (1-i)*p
                iz, oz = rot(s), op
                if ((iz[0] + oz[0]) % q, (iz[1] + oz[1]) % q) in S:
                    ok = False
                    break
                # p as leg u:   v = i*p + (1-i)*s
                oz = omi(s)
                if ((ip[0] + oz[0]) % q, (ip[1] + oz[1]) % q) in S:
                    ok = False
                    break
                # p as the third point v:  u = i^{-1}(p - (1-i)s)
                oz = omi(s)
                t = ((p[0] - oz[0]) % q, (p[1] - oz[1]) % q)
                u = irot(t)
                if u in S and u != s:
                    ok = False
                    break
            if ok:
                S.add(p)
        if len(S) > len(best):
            best = sorted(S)
    return best


def verify(T, q):
    """complete independent check"""
    S = set(T)
    rot, omi, _ = make_ops(q)
    bad = 0
    for b in S:
        ob = omi(b)
        for u in S:
            if u == b:
                continue
            iu = rot(u)
            if ((iu[0] + ob[0]) % q, (iu[1] + ob[1]) % q) in S:
                bad += 1
    return bad


EXACT = {2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 8, 8: 9, 9: 11, 10: 12, 11: 16}

if __name__ == "__main__":
    rng = random.Random(31337)
    qs = [int(a) for a in sys.argv[1:]] or [5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25,
                                            27, 29, 31, 35, 37, 41, 45, 49, 53, 59, 64]
    print(f"{'q':>4} {'g_lower':>8} {'exact':>6} {'log g/log q':>12} {'g/q':>6} {'viol':>5}")
    bestexp = 0.0
    for q in qs:
        restarts = max(8, min(300, 400000 // (q * q)))
        T = greedy(q, restarts, rng)
        v = verify(T, q)
        e = math.log(len(T)) / math.log(q)
        bestexp = max(bestexp, e)
        ex = EXACT.get(q, "")
        flag = ""
        if ex != "" and len(T) > ex:
            flag = "  *** EXCEEDS EXACT VALUE -- BUG"
        print(f"{q:>4} {len(T):>8} {str(ex):>6} {e:>12.4f} {len(T)/q:>6.2f} {v:>5}{flag}")
    print(f"\nbest exponent found: {bestexp:.4f}   (2.0 would kill the route; "
          f"1.0 is the trivial line)")
