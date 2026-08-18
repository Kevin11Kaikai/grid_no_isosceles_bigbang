#!/usr/bin/env python3
"""Structure mining for Route C extremal sets. Exact integer arithmetic only."""
import sys, itertools, collections


def parse_sets(path):
    """Each line: 'SET x,y x,y ...' or a bare list of x,y pairs."""
    out = []
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        if line.startswith('SET'):
            line = line[3:]
        elif not line[0].isdigit():
            continue
        toks = line.replace(',', ' ').split()
        try:
            v = [int(t) for t in toks]
        except ValueError:
            continue
        if len(v) < 4 or len(v) % 2:
            continue
        out.append(tuple(sorted((v[i], v[i+1]) for i in range(0, len(v), 2))))
    return out


def valid(pts):
    for a, b, c in itertools.permutations(pts, 3):
        if (a[0]-b[0])**2+(a[1]-b[1])**2 == (b[0]-c[0])**2+(b[1]-c[1])**2:
            return False
    return True


def canon(pts, n):
    best = None
    for f in range(8):
        q = []
        for (x, y) in pts:
            X, Y = x, y
            if f & 1: X = n-1-X
            if f & 2: Y = n-1-Y
            if f & 4: X, Y = Y, X
            q.append((X, Y))
        q = tuple(sorted(q))
        if best is None or q < best:
            best = q
    return best


def line_occupancy(pts, n, dx, dy):
    """Bucket points by the line of direction (dx,dy) they lie on.
    Invariant of a line: dy*x - dx*y."""
    c = collections.Counter(dy*x - dx*y for (x, y) in pts)
    # number of distinct lines of this direction that meet the n x n box
    vals = set(dy*x - dx*y for x in range(n) for y in range(n))
    return c, len(vals)


def stats(pts, n, label=''):
    S = set(pts)
    out = {}
    rows = collections.Counter(x for x, y in pts)
    cols = collections.Counter(y for x, y in pts)
    out['size'] = len(pts)
    out['rowocc'] = sorted(rows.values(), reverse=True)
    out['colocc'] = sorted(cols.values(), reverse=True)
    out['emptyrows'] = n - len(rows)
    out['emptycols'] = n - len(cols)
    out['maxrow'] = max(rows.values())
    out['maxcol'] = max(cols.values())
    dirs = {'(1,1)': (1, 1), '(1,-1)': (1, -1), '(1,2)': (1, 2), '(1,3)': (1, 3), '(2,1)': (2, 1),
            '(1,0)': (1, 0), '(0,1)': (0, 1)}
    out['dirs'] = {}
    for name, (dx, dy) in dirs.items():
        c, tot = line_occupancy(pts, n, dx, dy)
        out['dirs'][name] = (sorted(c.values(), reverse=True), tot - len(c), tot)
    # distance multiplicities
    dm = collections.Counter()
    for a, b in itertools.combinations(pts, 2):
        dm[(a[0]-b[0])**2+(a[1]-b[1])**2] += 1
    out['npairs'] = sum(dm.values())
    out['ndist'] = len(dm)
    out['distmult'] = dm
    # autocorrelation |S cap (S-v)|
    ac = collections.Counter()
    for a in pts:
        for b in pts:
            if a != b:
                ac[(b[0]-a[0], b[1]-a[1])] += 1
    out['autocorr'] = ac
    # convex-hull-ish: boundary occupancy
    out['on_border'] = sum(1 for x, y in pts if x in (0, n-1) or y in (0, n-1))
    out['corners'] = sum(1 for x, y in pts if x in (0, n-1) and y in (0, n-1))
    # is it a graph of a function (<=1 per column / per row)?
    out['is_perm_like'] = (out['maxrow'] <= 1, out['maxcol'] <= 1)
    # Sidon test: all pairwise differences distinct (as vectors up to sign)?
    out['sidon_vec'] = max(ac.values())
    return out


def main():
    n = int(sys.argv[1])
    sets = []
    for p in sys.argv[2:]:
        sets += parse_sets(p)
    print("read %d sets" % len(sets))
    seen = {}
    for s in sets:
        assert valid(s), "INVALID SET %s" % (s,)
        seen.setdefault(canon(s, n), s)
    print("distinct up to D4 symmetry: %d" % len(seen))
    agg_row, agg_dist, agg_ac = collections.Counter(), collections.Counter(), collections.Counter()
    emptyrows = collections.Counter()
    maxrows = collections.Counter()
    dirsum = collections.defaultdict(collections.Counter)
    border = collections.Counter()
    for s in seen.values():
        st = stats(s, n)
        agg_row[tuple(st['rowocc'])] += 1
        emptyrows[(st['emptyrows'], st['emptycols'])] += 1
        maxrows[(st['maxrow'], st['maxcol'])] += 1
        border[st['on_border']] += 1
        for r, m in st['distmult'].items():
            agg_dist[r] += m
        for v, m in st['autocorr'].items():
            agg_ac[v] += m
        for name, (occ, empty, tot) in st['dirs'].items():
            dirsum[name][(max(occ), empty)] += 1
    ex = list(seen.values())[0]
    st = stats(ex, n)
    print("\n--- example set (canonical-ish) ---")
    print(sorted(ex))
    for k in ('size', 'rowocc', 'colocc', 'emptyrows', 'emptycols', 'maxrow', 'maxcol',
              'npairs', 'ndist', 'on_border', 'corners', 'is_perm_like', 'sidon_vec'):
        print("  %-12s %s" % (k, st[k]))
    print("  directions (occupancy profile, #empty lines, #lines):")
    for name in ('(1,0)', '(0,1)', '(1,1)', '(1,-1)', '(1,2)', '(1,3)', '(2,1)'):
        print("     %-7s %s" % (name, st['dirs'][name]))
    print("\n--- aggregate over %d symmetry classes ---" % len(seen))
    print("row-occupancy profiles:", agg_row.most_common(12))
    print("(empty rows, empty cols):", sorted(emptyrows.items()))
    print("(max row, max col):", sorted(maxrows.items()))
    print("points on border:", sorted(border.items()))
    print("direction max-occupancy / #empty lines:")
    for name in ('(1,1)', '(1,-1)', '(1,2)', '(1,3)', '(2,1)'):
        print("   %-7s %s" % (name, sorted(dirsum[name].items())))
    tot = sum(agg_dist.values())
    print("\ntop squared distances by total multiplicity (out of %d pairs):" % tot)
    for r, m in agg_dist.most_common(20):
        print("   r^2=%-4d  %6d  (%.2f%%)" % (r, m, 100.0*m/tot))
    print("least popular realised squared distances:")
    for r, m in sorted(agg_dist.items(), key=lambda kv: kv[1])[:10]:
        print("   r^2=%-4d  %6d" % (r, m))
    print("\ntop autocorrelation vectors v (|S cap (S-v)| summed over classes):")
    for v, m in agg_ac.most_common(15):
        print("   v=%-10s %6d" % (str(v), m))


if __name__ == '__main__':
    main()
