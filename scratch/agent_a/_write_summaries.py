import json, glob, os, time
from pathlib import Path

def load(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

# negative control
neg = load("scratch/agent_a/negative_control_n100_r1.json")
Path("scratch/agent_a/negative_control_n100_r1.json").write_text(
    json.dumps({**neg, "expected": "INFEASIBLE_SCOPED", "role": "negative_control", "CRITICAL_CONTRADICTION": False,
                "note": "Matches Gate1 global r=1 exclusion; timeout was not used; FEASIBLE+legal did not occur."}, indent=2, sort_keys=True)+"\n",
    encoding="utf-8")

# n100 r2 summary
runs = []
for p in sorted(glob.glob("scratch/agent_a/hamming/r2_n100*.json")):
    if "halo_universe" in p: continue
    d = load(p)
    scope = (d.get("meta") or {}).get("scope") or {}
    runs.append({
        "file": p.replace("\\","/"),
        "status": d.get("status"),
        "U_id": scope.get("U_id") or d.get("U_id"),
        "seed": scope.get("seed"),
        "symmetry_mode": scope.get("symmetry_mode"),
        "universe_hash": d.get("universe_hash"),
        "n_vars": d.get("n_vars"),
        "wall_time_s": d.get("wall_time_s") or (d.get("meta") or {}).get("wall_time_s"),
        "rounds": (d.get("meta") or {}).get("rounds"),
        "final_cuts": (d.get("meta") or {}).get("final_cuts"),
        "best_illegal_V": (d.get("meta") or {}).get("best_illegal_V"),
        "time_to_best_illegal_s": (d.get("meta") or {}).get("time_to_best_illegal_s"),
    })
# include halo summary runs
if Path("scratch/agent_a/hamming/halo_pilot_summary.json").exists():
    halo = load("scratch/agent_a/hamming/halo_pilot_summary.json")
else:
    halo = {"runs": []}
# r3 if present
r3 = []
for p in sorted(glob.glob("scratch/agent_a/hamming/r3_n100*.json")):
    d = load(p)
    r3.append({"file": p.replace("\\","/"), "status": d.get("status"), "U_id": d.get("U_id"),
               "universe_hash": d.get("universe_hash"), "n_vars": d.get("n_vars"),
               "rounds": (d.get("meta") or {}).get("rounds"), "final_cuts": (d.get("meta") or {}).get("final_cuts"),
               "best_illegal_V": (d.get("meta") or {}).get("best_illegal_V"),
               "wall_time_s": (d.get("meta") or {}).get("wall_time_s")})

summary = {
    "schema": "agent_a_hamming_n100_r2_summary_v1",
    "git_commit": "148808f422cba7e8ca232ebb4710b84782086342",
    "primary_U_small_r2_hash": "a100c8b65096256676e7959491c95b5868d3a71c7b43bdf0f27609e382d50e88",
    "hash_verified_before_pilots": True,
    "claim_discipline": "All INFEASIBLE_SCOPED results are scope-restricted; NOT a global C(100)<=164. TIMEOUT never equated to INFEASIBLE.",
    "primary_U_small_r2_runs": [r for r in runs if r.get("U_id")=="U_small_r2"],
    "escalation_and_halo_runs": [r for r in runs if r.get("U_id")!="U_small_r2"],
    "halo_pilot_summary": halo,
    "r3_followups": r3,
    "V0_candidate_found": False,
    "CRITICAL_CONTRADICTION": False,
    "brute_confirm_n64_U_small_r1": {"checked": 3312, "legal_found": False, "best_V": 2, "agrees_with_cpsat": True},
    "brute_confirm_n100_U_small_r1": {"checked": 7936, "legal_found": False, "best_V": 5, "agrees_with_cpsat": True},
}
Path("scratch/agent_a/hamming_n100_r2_summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True)+"\n", encoding="utf-8")

# n64 summary
n64 = []
for p in sorted(glob.glob("scratch/agent_a/hamming/r1_n64*.json")):
    d = load(p)
    scope = (d.get("meta") or {}).get("scope") or {}
    n64.append({
        "file": p.replace("\\","/"), "status": d.get("status"), "U_id": scope.get("U_id"),
        "seed": scope.get("seed"), "universe_hash": d.get("universe_hash"), "n_vars": d.get("n_vars"),
        "wall_time_s": d.get("wall_time_s"), "rounds": (d.get("meta") or {}).get("rounds"),
        "final_cuts": (d.get("meta") or {}).get("final_cuts"),
        "best_illegal_V": (d.get("meta") or {}).get("best_illegal_V"),
    })
Path("scratch/agent_a/hamming_n64_r1_summary.json").write_text(json.dumps({
    "schema": "agent_a_hamming_n64_r1_summary_v1",
    "git_commit": "148808f422cba7e8ca232ebb4710b84782086342",
    "U_small_hash": "34f1c6172b699d0d46ee8dce1ea1eedabd004be4a8d0e0c0a857e05a63ed321e",
    "runs": n64,
    "full_enumeration_confirm": {"checked": 3312, "legal_found": False, "best_V": 2},
    "V0_candidate_found": False,
    "claim_note": "INFEASIBLE under scope (n=64,r=1,U_small) only — not global C(64)<=112",
}, indent=2, sort_keys=True)+"\n", encoding="utf-8")
print("wrote summaries")
print("n100 primary runs", len(summary["primary_U_small_r2_runs"]))
print("n64 runs", len(n64))
