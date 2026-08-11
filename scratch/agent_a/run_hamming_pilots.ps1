# Wave-2 Agent A pilot runner (reproducible commands)
# Prefer: .venv_solver\Scripts\python.exe
# Workers capped at 5 (~25% of 20 logical CPUs)
$ErrorActionPreference = "Stop"
$PY = ".venv_solver\Scripts\python.exe"
$MAN = "scratch/agent_a/manifest.jsonl"
$COMMIT = (git rev-parse HEAD).Trim()
Write-Host "git_commit=$COMMIT workers=5"

function Run-Hamming($n, $r, $uid, $seed, $budget, $sym, $out) {
  $ckpt = $out -replace '\.json$', '.ckpt.json'
  $ckpt = $ckpt -replace 'scratch/agent_a/', 'scratch/agent_a/checkpoints/'
  New-Item -ItemType Directory -Force -Path (Split-Path $ckpt) | Out-Null
  Write-Host "=== RUN $out seed=$seed budget=$budget sym=$sym ==="
  $t0 = Get-Date
  & $PY -m src.search.hamming_shell_conflict --n $n --r $r --u-id $uid --seed $seed `
    --time-budget-s $budget --per-round-s 45 --workers 5 --symmetry-mode $sym `
    --out $out --checkpoint $ckpt --manifest $MAN
  Write-Host "ELAPSED $(((Get-Date)-$t0).TotalSeconds)s for $out"
}

# n100 r=2 primary: 4 configs ~40-45 min each
Run-Hamming 100 2 U_small_r2 1 2700 asymmetric "scratch/agent_a/hamming/r2_n100_seed1.json"
Run-Hamming 100 2 U_small_r2 2 2700 asymmetric "scratch/agent_a/hamming/r2_n100_seed2.json"
Run-Hamming 100 2 U_small_r2 3 2700 asymmetric "scratch/agent_a/hamming/r2_n100_seed3.json"
Run-Hamming 100 2 U_small_r2 4 2700 symmetric "scratch/agent_a/hamming/r2_n100_seed4_sym.json"

# n64 r=1: 2 configs ~25-30 min
Run-Hamming 64 1 U_small 1 1800 asymmetric "scratch/agent_a/hamming/r1_n64_seed1.json"
Run-Hamming 64 1 U_small 2 1800 asymmetric "scratch/agent_a/hamming/r1_n64_seed2.json"

Write-Host "ALL HAMMING PILOTS DONE"
