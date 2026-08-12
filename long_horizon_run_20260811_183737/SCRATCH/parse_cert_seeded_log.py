#!/usr/bin/env python3
import json
import os
import re

LOG = r"C:\Users\YUS190\.cursor\projects\d-others-grid-no-isosceles-bigbang\terminals\936989.txt"
OUT = os.path.join(
    os.path.dirname(__file__),
    "..",
    "EXPERIMENTS",
    "LH3_cert_seeded",
    "cert_seeded_minv_partial.json",
)


def main():
    t = open(LOG, encoding="utf-8", errors="replace").read()
    parts = t.split('\n{\n  "q1"')
    rows = []
    for p in parts[1:]:
        block = '{\n  "q1"' + p
        m = re.search(r'"best_V": (\d+)', block)
        m2 = re.search(r'"V_seed": (\d+)', block)
        m3 = re.search(r'"status": "([^"]+)"', block)
        if m and m2:
            rows.append(
                {
                    "V_seed": int(m2.group(1)),
                    "best_V": int(m.group(1)),
                    "status": m3.group(1) if m3 else None,
                }
            )
    out = {
        "schema": "lh3_cert_seeded_minv_partial_v1",
        "n_rows_parsed": len(rows),
        "min_V_seed": min((r["V_seed"] for r in rows), default=None),
        "min_best_V": min((r["best_V"] for r in rows), default=None),
        "n_legal": sum(1 for r in rows if r["status"] == "FEASIBLE_LEGAL"),
        "note": "Partial — long run stopped; no V=0 in streamed trials.",
        "rows_summary": rows,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(
        json.dumps(
            {k: out[k] for k in out if k != "rows_summary"},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
