"""Tiny isosceles checker. Sanity only: iso-free ⇒ sq-free. Exact squared distances."""


def is_iso_free(pts):
    P = [tuple(p) for p in pts]
    for b in P:
        seen = set()
        for a in P:
            if a == b:
                continue
            r2 = (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2
            if r2 in seen:
                return False
            seen.add(r2)
    return True
