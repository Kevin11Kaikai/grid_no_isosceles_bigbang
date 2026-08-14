# connection_failed handoff (2026-08-14)

Previous long-horizon orchestrator **e09ce853** died with **Connection failed repeatedly**.

- Recovered from disk; did **not** restart the project.
- Incumbents unchanged: n=64 **112**, n=100 **164**. No legal +1.
- Harvested completed I/J/K/L JSON that was untracked at crash (see F077–F080).
- `summary_IJ.json` only recorded phase I; J/K/L result files were already on disk.
- K/L generator scripts were not saved (crash); results taken from JSON evidence only.

Next: new destroy+refill / exact micros **outside** S0-snap and midset/forbid ≤139.
Standing order: commit+push origin/master; no force-push; ignore `.venv_solver`.
