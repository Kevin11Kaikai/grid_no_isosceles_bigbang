"""Full Agent C Wave-2 red-team re-audit + B completion probe."""
from __future__ import annotations

import json
import re
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple

import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.verification.conflict_metric import conflict_count  # noqa: E402
from src.verification.oracle_verifier import is_legal_pivot_method  # noqa: E402
from src.verification_independent.independent_verifier import verify_independent  # noqa: E402
from src.structures.candidate_io import sha256_of_points  # noqa: E402

OUT = Path(__file__).resolve().parent
Point = Tuple[int, int]


def _pts(points: Sequence[Sequence[int]]) -> List[Point]:
    return [(int(p[0]), int(p[1])) for p in points]


def verify_set(points: Sequence[Sequence[int]], n: int, target: int, claimed_V: Optional[int] = None) -> Dict[str, Any]:
    pts = _pts(points)
    uniq = len(set(pts))
    V = conflict_count(pts, n)
    ok_a, wit_a = is_legal_pivot_method(pts, n)
    ok_b, wit_b = verify_independent(pts, n)
    h = sha256_of_points(pts)
    return {
        "n": n,
        "len": len(pts),
        "unique": uniq,
        "target": target,
        "card_ok": len(pts) == target == uniq,
        "V": V,
        "claimed_V": claimed_V,
        "V_matches_claim": (claimed_V is None) or (V == claimed_V),
        "V0": V == 0,
        "legal_A": bool(ok_a),
        "legal_B": bool(ok_b),
        "hash": h,
        "A_witness": wit_a if not ok_a else None,
    }


def elite_V_from_name(path: Path) -> Optional[int]:
    m = re.search(r"_V(\d+)_", path.name)
    return int(m.group(1)) if m else None


def audit_agent_c_full() -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []
    report = (ROOT / "scratch/agent_c/agent_c_wave2_report.md").read_text(encoding="utf-8")
    n100 = json.loads((ROOT / "scratch/agent_c/n100_fixed165_summary.json").read_text(encoding="utf-8"))
    n64 = json.loads((ROOT / "scratch/agent_c/n64_fixed113_summary.json").read_text(encoding="utf-8"))
    meta = json.loads((ROOT / "scratch/agent_c/campaign_meta.json").read_text(encoding="utf-8"))
    reproduce = json.loads((ROOT / "scratch/agent_c/reproduce_best.json").read_text(encoding="utf-8"))

    # 1. Fixed cardinality on all summary + seed_results + checkpoints
    card_fail = []
    for summary, target in [(n100, 165), (n64, 113)]:
        for res in summary.get("results", []):
            pts = res.get("points") or []
            if pts and (len(pts) != target or len({tuple(p) for p in pts}) != target):
                card_fail.append({"where": f"summary_n{summary['n']}", "seed": res.get("seed"), "len": len(pts)})
    for p in (ROOT / "scratch/agent_c/seed_results").glob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        tgt = d.get("target_size")
        pts = d.get("points") or []
        if pts and (len(pts) != tgt or len({tuple(x) for x in pts}) != tgt):
            card_fail.append({"where": str(p.name), "len": len(pts), "tgt": tgt})
    for p in (ROOT / "scratch/agent_c/checkpoints/candidates").glob("*.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        # candidate schema may use size
        pts = d.get("points") or []
        size = d.get("size") or d.get("target_size")
        n = d.get("n")
        tgt = {100: 165, 64: 113}.get(n, size)
        if pts and tgt and (len(pts) != tgt or len({tuple(x) for x in pts}) != len(pts)):
            card_fail.append({"where": p.name, "len": len(pts), "tgt": tgt})

    # 2. Elite archive: recompute V for all elites; focus on best V=2/3
    elites = list((ROOT / "scratch/agent_c/elite_archive").glob("*.json"))
    elite_results = []
    v0_elites = []
    card_elite_fail = []
    V_mismatch = []
    best_elites = []
    for ep in sorted(elites):
        d = json.loads(ep.read_text(encoding="utf-8"))
        n = d["n"]
        tgt = {100: 165, 64: 113}[n]
        name_V = elite_V_from_name(ep)
        vr = verify_set(d["points"], n, tgt, claimed_V=name_V)
        elite_results.append({"file": ep.name, "n": n, "name_V": name_V, "V": vr["V"], "card_ok": vr["card_ok"], "hash": vr["hash"][:16]})
        if not vr["card_ok"]:
            card_elite_fail.append(ep.name)
        if vr["V0"]:
            v0_elites.append(ep.name)
        if name_V is not None and vr["V"] != name_V:
            V_mismatch.append({"file": ep.name, "name_V": name_V, "actual_V": vr["V"]})
        if name_V is not None and name_V <= 3:
            best_elites.append({"file": ep.name, **{k: vr[k] for k in ("n", "V", "card_ok", "V0", "legal_A", "legal_B", "hash")}})

    # Clean-room best summary points
    cleanroom = {
        "n100_seed101": verify_set(n100["results"][0]["points"], 100, 165, n100["results"][0]["best_V"]),
        "n64_seed201": verify_set(n64["results"][0]["points"], 64, 113, n64["results"][0]["best_V"]),
        "reproduce_1201": verify_set(reproduce["points"], 64, 113, reproduce["best_V"]),
    }
    # Also verify one mid-V elite if present
    mid = [e for e in elites if "_V10_" in e.name or "_V7_" in e.name]
    if mid:
        d = json.loads(mid[0].read_text(encoding="utf-8"))
        cleanroom[f"elite_{mid[0].name}"] = verify_set(d["points"], d["n"], {100: 165, 64: 113}[d["n"]], elite_V_from_name(mid[0]))

    # 3. V=0 claims
    any_v0 = n100.get("any_v0") or n64.get("any_v0") or reproduce.get("v0_found")
    manifest_v0 = False
    man_agree = True
    man_lines = 0
    for line in (ROOT / "scratch/agent_c/manifest.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        man_lines += 1
        rec = json.loads(line)
        if rec.get("v0_found"):
            manifest_v0 = True
        if not rec.get("incremental_exact_agree", True):
            man_agree = False

    # 4. TIMEOUT / global UB wording
    wording_blob = report + json.dumps(n100.get("note")) + json.dumps(n64.get("note"))
    has_global_ub = bool(re.search(r"C\s*\(\s*100\s*\)\s*[≤<=]\s*164|C\s*\(\s*64\s*\)\s*[≤<=]\s*112", wording_blob))
    claims_lb = "lower bound" in report.lower() and "no new lower bound" not in report.lower() and "not a lower-bound" not in wording_blob.lower()
    # Agent C is heuristic — no CP-SAT INFEAS/TIMEOUT status tokens expected
    status_tokens = set()
    for line in (ROOT / "scratch/agent_c/manifest.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            rec = json.loads(line)
            if "status" in rec:
                status_tokens.add(rec["status"])

    # 5. External-halo repair pool (code review)
    src = (ROOT / "src/search/fixed_cardinality_minconflict.py").read_text(encoding="utf-8")
    halo_checks = {
        "expanded_repair_pool_fn": "def expanded_repair_pool" in src,
        "never_S_only_doc": "Never uses S'-only" in src or "never S'-only" in src.lower() or "Never uses S'-only deletion" in src,
        "pool_includes_halo": "pools.halo" in src and "pools.add_pool" in src and "pools.easiest_blockers" in src,
        "pool_includes_recently_deleted": "recently_deleted" in src,
        "pool_policy_meta": "S_cup_halo_cup_deleted_cup_lowblocker" in src,
        "report_claims_external_halo": "Gate1 halo" in report or "S′ ∪ Gate1 halo" in report or "S' ∪ Gate1 halo" in report,
        "moves_use_external": "propose_1for1(state, external" in src and "propose_ejection_chain(state, external" in src,
    }
    # Prove pool not baseline-subset: load Gate1Pools sizes
    from src.search.fixed_cardinality_minconflict import load_gate1_pools

    pools100 = load_gate1_pools(100)
    pools64 = load_gate1_pools(64)
    base100 = set(pools100.baseline)
    ext100 = set(pools100.external_candidates())
    outside_baseline_100 = len([p for p in ext100 if p not in base100])
    outside_baseline_64 = len([p for p in set(pools64.external_candidates()) if p not in set(pools64.baseline)])
    halo_checks["external_outside_baseline_n100"] = outside_baseline_100
    halo_checks["external_outside_baseline_n64"] = outside_baseline_64
    halo_checks["halo_size_n100"] = len(pools100.halo)
    halo_checks["halo_size_n64"] = len(pools64.halo)
    halo_ok = (
        all(halo_checks[k] for k in [
            "expanded_repair_pool_fn", "pool_includes_halo", "pool_includes_recently_deleted",
            "pool_policy_meta", "report_claims_external_halo", "moves_use_external",
        ])
        and outside_baseline_100 > 0
        and outside_baseline_64 > 0
    )

    # 6. Ownership / protected writes
    st = subprocess.check_output(["git", "status", "--short"], cwd=str(ROOT), text=True)
    protected = []
    for ln in st.splitlines():
        path = ln[3:].strip().replace("\\", "/")
        for prot in [
            "src/verification/oracle_verifier.py",
            "src/verification_independent/",
            "data/baselines/",
            "results/certified/",
        ]:
            if path.startswith(prot.rstrip("/")) or path.startswith(prot):
                if not path.startswith("??"):  # new untracked under protected is still concerning if certified
                    protected.append(ln)
                elif "results/certified" in path:
                    protected.append(ln)

    # Move stats show repair_accept > 0 on campaign seeds (repair operator used)
    repair_used = all(
        (r.get("move_stats") or {}).get("repair_accept", 0) > 0
        for r in n100["results"] + n64["results"]
    )

    checks = {
        "1_fixed_cardinality": {
            "pass": len(card_fail) == 0 and len(card_elite_fail) == 0,
            "summary_seed_checkpoint_fails": card_fail,
            "elite_fails": card_elite_fail,
        },
        "2_incremental_vs_exact_elites": {
            "pass": (
                n100.get("incremental_exact_agree_all") is True
                and n64.get("incremental_exact_agree_all") is True
                and man_agree
                and len(V_mismatch) == 0
                and all(cleanroom[k]["V_matches_claim"] for k in cleanroom)
            ),
            "summary_agree": {
                "n100": n100.get("incremental_exact_agree_all"),
                "n64": n64.get("incremental_exact_agree_all"),
                "manifest_all_agree": man_agree,
            },
            "elite_name_V_mismatches": V_mismatch,
            "n_elites_checked": len(elites),
            "best_elites_sample": best_elites[:8],
            "cleanroom": {k: {kk: vv for kk, vv in v.items() if kk != "A_witness"} for k, v in cleanroom.items()},
        },
        "3_no_v0": {
            "pass": (not any_v0) and (not manifest_v0) and len(v0_elites) == 0 and not any(cleanroom[k]["V0"] for k in cleanroom),
            "summary_any_v0": any_v0,
            "manifest_v0": manifest_v0,
            "v0_elite_files": v0_elites,
            "report_claims_none": "No V=0" in report,
            "min_elite_V_n100": min((e["V"] for e in elite_results if e["n"] == 100), default=None),
            "min_elite_V_n64": min((e["V"] for e in elite_results if e["n"] == 64), default=None),
        },
        "4_timeout_wording": {
            "pass": (not has_global_ub) and ("no new lower bound" in report.lower() or "Not claimed" in report),
            "has_global_ub_wording": has_global_ub,
            "manifest_status_tokens": sorted(status_tokens),
            "note": "Heuristic search; no CP-SAT TIMEOUT/INFEASIBLE statuses in Agent C I/O",
            "summary_notes_ok": "not a lower-bound" in (n100.get("note", "") + n64.get("note", "")).lower(),
        },
        "5_external_halo_repair": {
            "pass": halo_ok and repair_used,
            "code_checks": halo_checks,
            "repair_accept_all_seeds": repair_used,
        },
        "6_no_protected_writes": {
            "pass": len(protected) == 0,
            "protected_hits": protected,
        },
    }

    overall = all(checks[k]["pass"] for k in checks)
    for cid, c in checks.items():
        if not c["pass"]:
            findings.append({"id": cid, "severity": "FAIL", "detail": c})

    return {
        "status": "COMPLETE",
        "verdict": "PASS" if overall else "FAIL",
        "critical_flaws": False if overall else True,
        "report_present": True,
        "campaign_wall_s": meta.get("campaign_wall_s"),
        "manifest_lines": man_lines,
        "n_elites": len(elites),
        "best_V": {"n100": n100.get("best_V"), "n64": n64.get("best_V"), "reproduce": reproduce.get("best_V")},
        "checks": checks,
        "findings": findings,
        "repair_required": [],
    }


def probe_agent_b() -> Dict[str, Any]:
    report = ROOT / "scratch/agent_b/agent_b_wave2_report.md"
    files = [p.name for p in (ROOT / "scratch/agent_b").glob("*") if p.is_file()]
    resume = ROOT / "scratch/agent_b/wave2_resume.log"
    tail = None
    if resume.exists():
        raw = resume.read_bytes()
        for enc in ("utf-8", "utf-16", "utf-16-le", "cp1252", "latin-1"):
            try:
                tail = raw.decode(enc)[-600:]
                break
            except Exception:
                continue
    # latest mid/long checkpoints
    ckpts = sorted((ROOT / "scratch/agent_b/checkpoints").glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    latest = []
    for p in ckpts[:5]:
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            latest.append({
                "file": p.name,
                "solver_status": d.get("solver_status") or d.get("status"),
                "pilot_tag": d.get("pilot_tag"),
                "wall_time_s": d.get("wall_time_s") or d.get("pilot_wall_time_s"),
            })
        except Exception:
            latest.append({"file": p.name, "error": True})
    complete = report.exists()
    return {
        "status": "COMPLETE" if complete else "PENDING_INCOMPLETE",
        "final_report_present": complete,
        "top_level_files": files,
        "resume_log_tail": tail,
        "latest_checkpoints": latest,
        "note": None if complete else "agent_b_wave2_report.md still absent; keep B PENDING",
    }


def main() -> None:
    c = audit_agent_c_full()
    b = probe_agent_b()
    (OUT / "agent_c_full_checks.json").write_text(json.dumps(c, indent=2), encoding="utf-8")
    (OUT / "agent_b_status_probe.json").write_text(json.dumps(b, indent=2), encoding="utf-8")
    print("C verdict", c["verdict"], "critical", c["critical_flaws"])
    for k, v in c["checks"].items():
        print(" ", k, "PASS" if v["pass"] else "FAIL")
    print("best elites", c["checks"]["2_incremental_vs_exact_elites"]["best_elites_sample"][:3])
    print("halo outside baseline", c["checks"]["5_external_halo_repair"]["code_checks"]["external_outside_baseline_n100"])
    print("B status", b["status"], "report", b["final_report_present"])
    if b.get("resume_log_tail"):
        print("B resume tail:", repr(b["resume_log_tail"][-200:]))


if __name__ == "__main__":
    main()
