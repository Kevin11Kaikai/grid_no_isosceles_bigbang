"""Run dense four-fold census, independent Q4-greedy check, J1, and B4′ gate."""
from __future__ import annotations

import json
import random
from collections import Counter
from pathlib import Path

from census import census_triples, classify_uv, is_q4_survivor, summarize
from fourfold import (
    dense_fourfold,
    dense_fourfold_freq_search,
    dense_fourfold_from_bases,
    is_3ap_free,
)
from iso import is_iso_free
from joint import (
    J1_holds_if_q4_plus_extra,
    embed_rot90_fourfold,
    extra_linekill_subset,
    project,
    rot90_q4_survivor_family,
    rot90_stencils,
)
from q4 import greedy, verify
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


def dump_json(name, obj):
    p = OUT / name
    p.write_text(json.dumps(obj, indent=2), encoding="utf-8")
    return p


def rec_public(rec):
    skip = {"set", "A", "B", "W", "Z"}
    return {k: v for k, v in rec.items() if k not in skip}


def killed_by_forms(u, v, forms):
    ux, uy = u
    vx, vy = v
    hits = []
    for name, psi in forms:
        U, V = psi(ux, uy), psi(vx, vy)
        if U == V != 0:
            hits.append((name, "P1"))
        if U + 2 * V == 0 and U != 0:
            hits.append((name, "P2"))
        if 2 * U + V == 0 and V != 0:
            hits.append((name, "P3"))
    return hits


def run_fourfold_census(seed=20260816):
    rng = random.Random(seed)
    results = []
    for n in (16, 20, 24, 32, 40, 48, 64):
        n_tries = 40 if n <= 32 else 24
        rec_f = dense_fourfold_freq_search(n, rng, n_tries=n_tries)
        rec_i = dense_fourfold_from_bases(n, rng, n_tries=max(12, n_tries // 2))
        rec_s = dense_fourfold(n, rng, n_tries=max(12, n_tries // 2))
        chosen = rec_f
        for alt in (rec_i, rec_s):
            if alt is not None and alt["|S|"] > chosen["|S|"]:
                chosen = alt
        pts = chosen["set"]
        q4_ok = verify(n, pts)
        rows = census_triples(pts)
        summ = summarize(rows)
        j1 = rot90_stencils(pts)
        entry = {
            **rec_public(chosen),
            "q4": q4_ok,
            "iso_free": is_iso_free(pts),
            "census": summ,
            "J1_count": len(j1),
            "J1_fires": len(j1) > 0,
            "J1_q4_survivor_count": sum(1 for h in j1 if h["q4_survivor"]),
        }
        results.append(entry)
        print(
            f"fourfold n={n:3d} kind={chosen.get('kind')} |S|={chosen['|S|']:4d} "
            f"q4={q4_ok} iso_free={entry['iso_free']} triples={summ['n_triples']} "
            f"surv={summ['n_survivors']} killed={summ['n_killed_by_q4_forms']} "
            f"J1={len(j1)}"
        )
        if summ["n_killed_by_q4_forms"]:
            print("  WARNING: four-fold triple classified as P1-P3 on a Q4 form")
        if summ["top_survivor_uv"][:8]:
            print("  top survivor (u,v):", summ["top_survivor_uv"][:8])
    dump_json("fourfold_census.json", results)
    return results


def run_q4_greedy_census(seed=7):
    results = []
    agg_uv = Counter()
    agg_rot = Counter()
    for n, n_sets in ((16, 8), (20, 6), (24, 6), (32, 4), (40, 3)):
        sets = sample_q4_greedy(n, n_sets, seed + n)
        for rec in sets:
            pts = rec["set"]
            rows = census_triples(pts)
            summ = summarize(rows)
            j1 = rot90_stencils(pts)
            for r in rows:
                if r["survivor"]:
                    key = tuple(sorted((r["u"], r["v"])))
                    agg_uv[key] += 1
                    if r["rot90"]:
                        agg_rot[key] += 1
            entry = {
                "n": n,
                "i": rec["i"],
                "|S|": rec["|S|"],
                "q4": rec["q4"],
                "iso_free": is_iso_free(pts),
                "census": summ,
                "J1_count": len(j1),
                "J1_fires": len(j1) > 0,
            }
            results.append(entry)
        fires = sum(1 for e in results if e["n"] == n and e["J1_fires"])
        ntri = sum(e["census"]["n_triples"] for e in results if e["n"] == n)
        nsurv = sum(e["census"]["n_survivors"] for e in results if e["n"] == n)
        nrot = sum(e["census"]["n_rot90_survivors"] for e in results if e["n"] == n)
        print(
            f"q4-greedy n={n:3d} sets={n_sets} J1_fires={fires}/{n_sets} "
            f"|S|~{sum(e['|S|'] for e in results if e['n']==n)/n_sets:.1f} "
            f"triples={ntri} surv={nsurv} rot90_surv={nrot}"
        )
    dump_json("q4_greedy_census.json", results)
    dump_json(
        "q4_greedy_survivor_agg.json",
        {
            "top_survivor_uv": [[list(k), c] for k, c in agg_uv.most_common(40)],
            "top_rot90_survivor_uv": [[list(k), c] for k, c in agg_rot.most_common(40)],
            "n_distinct_survivor_uv": len(agg_uv),
            "n_distinct_rot90_survivor_uv": len(agg_rot),
        },
    )
    return results


def run_j1_embed():
    """Explicit four-fold (3 points) for the smallest Q4-surviving rot90 stencils."""
    fam = rot90_q4_survivor_family(pmax=8)
    embeds = []
    for u, v in fam[:40]:
        p, q = u
        rec = embed_rot90_fourfold(p, q)
        if rec is None:
            continue
        pts = rec["set"]
        n = rec["n"]
        rec_pub = rec_public(rec)
        rec_pub.update(
            {
                "q4": verify(n, pts),
                "J1_fires": len(rot90_stencils(pts)) > 0,
                "iso_free": is_iso_free(pts),
                "q4_form_hits": classify_uv(u, v),
                "projections_3ap_free": all(
                    rec[k] for k in ("A_3ap_free", "B_3ap_free", "W_3ap_free", "Z_3ap_free")
                ),
            }
        )
        embeds.append(rec_pub)
    dump_json("j1_fourfold_embeds.json", embeds)
    ok = [e for e in embeds if e["q4"] and e["J1_fires"] and e["projections_3ap_free"]]
    print(f"J1 four-fold embeds: {len(ok)}/{len(embeds)} fire J1, Q4-ok, 3-AP-free projections")
    if ok:
        print("  example", ok[0]["u"], ok[0]["v"], "pts n=", ok[0]["n"])
    return embeds


def run_b4_gate(seed=99):
    rng = random.Random(seed)
    n = 32
    rec = dense_fourfold_freq_search(n, rng, n_tries=40)
    pts = rec["set"]
    assert verify(n, pts)
    j1 = rot90_stencils(pts)
    explained, leftover = J1_holds_if_q4_plus_extra(pts, EXTRA_FORMS)
    extra_trials = []
    for e in ((2, 1), (1, 2), (2, -1), (1, -2), (3, 1), (1, 3), (3, 2), (2, 3)):
        kept = extra_linekill_subset(n, pts, e, rng)
        still = rot90_stencils(kept)
        extra_trials.append(
            {
                "e": e,
                "|S|": len(pts),
                "|S5|": len(kept),
                "proj_3ap_free": is_3ap_free(project(kept, e)),
                "J1_before": len(j1),
                "J1_after": len(still),
                "J1_still_fires": len(still) > 0,
            }
        )

    rng2 = random.Random(seed + 1)
    gpts = list(greedy(n, rng2))
    g_explained, g_left = J1_holds_if_q4_plus_extra(gpts, EXTRA_FORMS)
    g_j1 = rot90_stencils(gpts)
    g_trials = []
    for e in ((2, 1), (1, 2), (2, -1), (1, -2), (3, 1), (1, 3)):
        kept = extra_linekill_subset(n, gpts, e, rng2)
        still = rot90_stencils(kept)
        g_trials.append(
            {
                "e": e,
                "|S|": len(gpts),
                "|S5|": len(kept),
                "J1_before": len(g_j1),
                "J1_after": len(still),
                "J1_still_fires": len(still) > 0,
            }
        )

    # Family-level: a fixed finite extra-form list cannot P1–P3-kill all rot90 Q4-survivors.
    fam = rot90_q4_survivor_family(pmax=10)
    fam_left = []
    for u, v in fam:
        if not killed_by_forms(u, v, EXTRA_FORMS):
            fam_left.append((u, v))

    # Five-fold witness: embed a leftover stencil; its five projections are 3-AP-free.
    five_fold_witness = None
    for u, v in fam_left:
        rec_e = embed_rot90_fourfold(u[0], u[1])
        if rec_e is None:
            continue
        if not all(
            rec_e[k] for k in ("A_3ap_free", "B_3ap_free", "W_3ap_free", "Z_3ap_free")
        ):
            continue
        e5 = (2, 1)
        vals = project(rec_e["set"], e5)
        if is_3ap_free(vals) and verify(rec_e["n"], rec_e["set"]) and rot90_stencils(rec_e["set"]):
            five_fold_witness = {
                **rec_public(rec_e),
                "e5": e5,
                "phi5_3ap_free": True,
                "q4": True,
                "J1_fires": True,
            }
            break

    report = {
        "fourfold_dense": {
            **rec_public(rec),
            "q4": True,
            "J1_count": len(j1),
            "extra_forms_explain_all_J1": explained,
            "n_J1_surviving_extra_forms": len(leftover),
            "leftover_uv": [(h["u"], h["v"]) for h in leftover[:30]],
            "fifth_projection_trials": extra_trials,
        },
        "q4_greedy": {
            "n": n,
            "|S|": len(gpts),
            "J1_count": len(g_j1),
            "extra_forms_explain_all_J1": g_explained,
            "n_J1_surviving_extra_forms": len(g_left),
            "leftover_uv": [(h["u"], h["v"]) for h in g_left[:20]],
            "fifth_projection_trials": g_trials,
        },
        "family": {
            "n_rot90_q4_survivors_pmax10": len(fam),
            "n_not_killed_by_extra_forms": len(fam_left),
            "sample_leftover": fam_left[:15],
            "verdict": (
                "J1 is not a restatement of a fixed extra-projection list"
                if fam_left
                else "DEAD_B4: extra forms kill the whole small rot90 family"
            ),
        },
        "five_fold_witness": five_fold_witness,
    }
    dump_json("b4_gate.json", report)
    print(
        "B4′ dense four-fold |S|=",
        rec["|S|"],
        "J1=",
        len(j1),
        "explained_by_extra=",
        explained,
    )
    print(
        "B4′ q4-greedy |S|=",
        len(gpts),
        "J1=",
        len(g_j1),
        "explained_by_extra=",
        g_explained,
        "leftover",
        len(g_left),
    )
    print(
        "B4′ family leftover",
        len(fam_left),
        "/",
        len(fam),
        "five_fold_witness",
        five_fold_witness is not None,
    )
    return report


if __name__ == "__main__":
    print("=== dense four-fold census ===")
    run_fourfold_census()
    print("=== independent Q4-greedy census ===")
    run_q4_greedy_census()
    print("=== J1 four-fold embeds ===")
    run_j1_embed()
    print("=== B4′ gate ===")
    run_b4_gate()
    print("done")
