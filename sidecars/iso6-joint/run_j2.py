"""Census non-J1 leftovers on dense four-fold and Q4-greedy."""
from __future__ import annotations

import json
import random
from pathlib import Path

from fourfold import dense_fourfold_freq_search
from j2 import census_j2
from q4 import verify
from q4_greedy import sample_q4_greedy

OUT = Path(__file__).resolve().parent / "out"
OUT.mkdir(exist_ok=True)

EXTRA_FORMS = (
    ("2x+y", lambda dx, dy: 2 * dx + dy),
    ("x+2y", lambda dx, dy: dx + 2 * dy),
    ("2x-y", lambda dx, dy: 2 * dx - dy),
    ("x-2y", lambda dx, dy: dx - 2 * dy),
    ("3x+y", lambda dx, dy: 3 * dx + dy),
    ("x+3y", lambda dx, dy: dx + 3 * dy),
)


def killed_by_extra(u, v):
    ux, uy = u
    vx, vy = v
    for _name, psi in EXTRA_FORMS:
        U, V = psi(ux, uy), psi(vx, vy)
        if U == V != 0 or (U + 2 * V == 0 and U != 0) or (2 * U + V == 0 and V != 0):
            return True
    return False


def embed_three(u, v):
    """Three-point set {0, u, v} shifted into the first quadrant."""
    pts0 = [(0, 0), u, v]
    minx = min(p[0] for p in pts0)
    miny = min(p[1] for p in pts0)
    pts = [(p[0] - minx, p[1] - miny) for p in pts0]
    n = 1 + max(max(p[0] for p in pts), max(p[1] for p in pts))
    A = sorted({p[0] for p in pts})
    B = sorted({p[1] for p in pts})
    W = sorted({p[0] + p[1] for p in pts})
    Z = sorted({p[0] - p[1] for p in pts})
    from fourfold import is_3ap_free

    return {
        "n": n,
        "u": u,
        "v": v,
        "set": pts,
        "A_3ap_free": is_3ap_free(A),
        "B_3ap_free": is_3ap_free(B),
        "W_3ap_free": is_3ap_free(W),
        "Z_3ap_free": is_3ap_free(Z),
        "fourfold_ok": is_3ap_free(A)
        and is_3ap_free(B)
        and is_3ap_free(W)
        and is_3ap_free(Z),
    }


def main():
    rng = random.Random(20260816)
    four = []
    for n in (16, 24, 32, 40, 48, 64):
        n_tries = 40 if n <= 32 else 20
        rec = dense_fourfold_freq_search(n, rng, n_tries=n_tries)
        pts = rec["set"]
        d = census_j2(f"fourfold_{n}", n, pts)
        d["kind"] = rec.get("kind")
        d["q4"] = verify(n, pts)
        d["|S|"] = rec["|S|"]
        four.append(d)
        print(
            f"FF n={n:3d} m={d['m']:3d} tri={d['n_triples']:3d} "
            f"J1={d['n_rot90_J1']:3d} ap3={d['n_ap3']:3d} "
            f"other={d['n_other']:3d} oth_surv={d['n_other_q4_survivors']:3d} "
            f"q4={d['q4']}",
            flush=True,
        )

    greedy_rows = []
    for n, n_sets in ((16, 4), (24, 3), (32, 3)):
        samples = sample_q4_greedy(n, n_sets, seed=100 + n)
        agg = {
            "n": n,
            "n_sets": n_sets,
            "fires_J1": 0,
            "fires_ap3": 0,
            "fires_other": 0,
            "sum_other_surv": 0,
            "sum_triples": 0,
            "samples": [],
        }
        for s in samples:
            d = census_j2(f"q4g_{n}_{s['i']}", n, s["set"])
            agg["fires_J1"] += int(d["fires_J1"])
            agg["fires_ap3"] += int(d["fires_ap3"])
            agg["fires_other"] += int(d["fires_other"])
            agg["sum_other_surv"] += d["n_other_q4_survivors"]
            agg["sum_triples"] += d["n_triples"]
            agg["samples"].append(
                {k: d[k] for k in d if k != "top_other_surv_uv"}
            )
        greedy_rows.append(agg)
        print(
            f"QG n={n:3d} J1={agg['fires_J1']}/{n_sets} "
            f"ap3={agg['fires_ap3']}/{n_sets} "
            f"other={agg['fires_other']}/{n_sets} "
            f"oth_surv_sum={agg['sum_other_surv']}",
            flush=True,
        )

    # 3-point embeds of top leftover other-uv from four-fold
    embeds = []
    seen = set()
    for d in four:
        for uv, _c in d["top_other_surv_uv"]:
            key = tuple(uv) if not isinstance(uv[0], (list, tuple)) else (
                tuple(uv[0]),
                tuple(uv[1]),
            )
            # uv from json-able most_common: ((x,y),(x,y))
            u, v = uv
            u, v = tuple(u), tuple(v)
            key = tuple(sorted((u, v)))
            if key in seen:
                continue
            seen.add(key)
            emb = embed_three(u, v)
            emb["extra_forms_kill"] = killed_by_extra(u, v)
            embeds.append(emb)
            if len(embeds) >= 24:
                break
        if len(embeds) >= 24:
            break

    n_embed_ff = sum(1 for e in embeds if e["fourfold_ok"])
    n_embed_unkilled = sum(
        1 for e in embeds if e["fourfold_ok"] and not e["extra_forms_kill"]
    )
    print(
        f"embeds {len(embeds)} fourfold_ok={n_embed_ff} "
        f"not_extra_killed={n_embed_unkilled}",
        flush=True,
    )

    summary = {
        "named_J2": None,
        "reason": (
            "No one-parameter stencil on all of Z^2 besides ±90° and 180° "
            "(collinear 3-AP). Non-J1 leftovers are generic equal-length pairs. "
            "Naming the whole leftover class is RF1 minus Q4, i.e. the original "
            "problem. J2 is therefore NOT named. Record the census only."
        ),
        "fourfold_any_other": any(d["n_other_q4_survivors"] > 0 for d in four),
        "fourfold_any_ap3": any(d["n_ap3"] > 0 for d in four),
        "greedy_any_other": any(g["fires_other"] > 0 for g in greedy_rows),
    }

    (OUT / "j2_fourfold.json").write_text(
        json.dumps(four, indent=2), encoding="utf-8"
    )
    (OUT / "j2_q4_greedy.json").write_text(
        json.dumps(greedy_rows, indent=2), encoding="utf-8"
    )
    (OUT / "j2_embeds.json").write_text(
        json.dumps(embeds, indent=2), encoding="utf-8"
    )
    (OUT / "j2_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print("wrote j2_*.json", flush=True)


if __name__ == "__main__":
    main()
