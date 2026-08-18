"""Case A with barely-large r(a), then maximise a second matching."""
from __future__ import annotations

import random

from q4 import FourDir, verify
from lemma3_search import overlap_stats, in_grid
from sprime_second import place_matching, rest_max_r


def main():
    rng = random.Random(1)
    print("n trial r_a R' |S'| |S*| thresh beat pc", flush=True)
    found = []
    for n in (32, 81, 128, 243):
        thresh = n ** 0.75
        need = int(thresh) + 2
        beat_any = False
        best_Rp = 0
        for trial in range(30):
            a = n - 1
            st = FourDir(n)
            pa = place_matching(st, n, a, rng, limit=need)
            c = rng.randrange(0, 2 * n - 1)
            if c == a:
                continue
            pc = place_matching(st, n, c, rng)
            # fill leftover singles
            cells = [(x, y) for x in range(n) for y in range(n)]
            rng.shuffle(cells)
            for x, y in cells:
                ks = st.can_add(x, y)
                if ks is not None:
                    st.push(x, y, ks)
            pts = set(st.pts)
            assert verify(n, pts)
            stt = overlap_stats(n, pts)
            a_used = stt["a_star"]
            Rp, nrest, nstar = rest_max_r(n, pts, a_used)
            if Rp > best_Rp:
                best_Rp = Rp
            beat = Rp > thresh
            if beat:
                beat_any = True
                rec = dict(n=n, trial=trial, pa=pa, pc=pc, r=stt["r_star"], Rp=Rp, rest=nrest, star=nstar)
                found.append(rec)
                print("BEAT", rec, flush=True)
        print(
            f"n={n} need={need} th={thresh:.1f} best_R'={best_Rp} beat={beat_any}",
            flush=True,
        )
    print("found", len(found), flush=True)


if __name__ == "__main__":
    main()
