"""Agent C Wave-2 campaign runner. Writes only under scratch/agent_c/."""
from __future__ import annotations

import json
import time
from pathlib import Path

from src.search.fixed_cardinality_minconflict import (
    SCRATCH,
    run_campaign,
    run_fixed_cardinality_search,
    write_summary,
    _result_to_dict,
)


def main() -> None:
    SCRATCH.mkdir(parents=True, exist_ok=True)
    campaign_t0 = time.time()
    workers = 5  # ~25% of 20 logical cores

    # n=100: 8 seeds × 25 min
    n100_seeds = [101, 102, 103, 104, 105, 106, 107, 108]
    t_n100 = 25 * 60.0
    print(f"[campaign] n100 start seeds={n100_seeds} time_per={t_n100}s workers={workers}", flush=True)
    t0 = time.time()
    res100 = run_campaign(100, n100_seeds, t_n100, max_workers=workers, scratch_dir=SCRATCH)
    wall100 = time.time() - t0
    p100 = write_summary(100, res100, SCRATCH, wall100)
    print(f"[campaign] n100 done wall={wall100:.1f}s best_V={res100[0].get('best_V') if res100 else None} -> {p100}", flush=True)

    # n=64: 4 seeds × 15 min
    n64_seeds = [201, 202, 203, 204]
    t_n64 = 15 * 60.0
    print(f"[campaign] n64 start seeds={n64_seeds} time_per={t_n64}s workers={workers}", flush=True)
    t0 = time.time()
    res64 = run_campaign(64, n64_seeds, t_n64, max_workers=min(workers, 4), scratch_dir=SCRATCH)
    wall64 = time.time() - t0
    p64 = write_summary(64, res64, SCRATCH, wall64)
    print(f"[campaign] n64 done wall={wall64:.1f}s best_V={res64[0].get('best_V') if res64 else None} -> {p64}", flush=True)

    # Optional reproduce of best overall if budget remains (< 5.5h)
    elapsed = time.time() - campaign_t0
    remaining = 5.5 * 3600 - elapsed
    reproduce = None
    if remaining >= 20 * 60:
        # pick better relative improvement seed
        candidates = []
        if res100 and res100[0].get("best_V") is not None:
            candidates.append(("100", res100[0]))
        if res64 and res64[0].get("best_V") is not None:
            candidates.append(("64", res64[0]))
        if candidates:
            # prefer absolute lowest V, tie-break n100
            tag, best = sorted(
                candidates,
                key=lambda x: (x[1]["best_V"], 0 if x[0] == "100" else 1),
            )[0]
            n = int(tag)
            seed = int(best["seed"]) + 1000  # distinct reproduce seed with same init
            init = best["init_method"]
            budget = min(30 * 60.0, remaining - 60)
            print(f"[campaign] reproduce n={n} seed={seed} init={init} budget={budget}s", flush=True)
            r = run_fixed_cardinality_search(
                n=n,
                seed=seed,
                time_budget_s=budget,
                init_method=init,
                n_replicas=3,
                scratch_dir=SCRATCH,
            )
            reproduce = _result_to_dict(r)
            (SCRATCH / "reproduce_best.json").write_text(
                json.dumps(reproduce, indent=2), encoding="utf-8"
            )
            print(f"[campaign] reproduce best_V={r.best_V} init_V={r.initial_V}", flush=True)

    meta = {
        "campaign_wall_s": time.time() - campaign_t0,
        "n100_summary": str(p100),
        "n64_summary": str(p64),
        "reproduce": reproduce,
        "workers": workers,
    }
    (SCRATCH / "campaign_meta.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(json.dumps(meta, indent=2), flush=True)


if __name__ == "__main__":
    main()
