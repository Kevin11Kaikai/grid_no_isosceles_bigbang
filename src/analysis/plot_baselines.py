"""Generate publication-quality (black-and-white-printable) figures for the two
certified baseline constructions. Run: python src/analysis/plot_baselines.py
Outputs to figures/.
"""
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
from data.baselines.official_raw import SOL_64, SOL_100

FIGDIR = os.path.join(os.path.dirname(__file__), "..", "..", "figures")
os.makedirs(FIGDIR, exist_ok=True)


def plot_points(points, n, title, out_path):
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(xs, ys, s=22, c="black", marker="o", zorder=3)
    ax.set_xlim(-0.5, n - 0.5)
    ax.set_ylim(-0.5, n - 0.5)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_title(f"{title}\n({len(points)} points on {n}x{n} grid)")
    tick_step = 10 if n >= 50 else 5
    ax.set_xticks(range(0, n, tick_step))
    ax.set_yticks(range(0, n, tick_step))
    ax.grid(True, linestyle="--", linewidth=0.4, color="gray", alpha=0.6)
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"saved {out_path}")


def plot_ring_histogram(points, n, title, out_path):
    def ring(p):
        x, y = p
        return min(x, y, n - 1 - x, n - 1 - y)

    rings = [ring(p) for p in points]
    max_ring = (n - 1) // 2
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.hist(rings, bins=range(0, max_ring + 2), color="black", rwidth=0.8)
    ax.set_xlabel("ring (Chebyshev distance to nearest grid edge)")
    ax.set_ylabel("number of selected points")
    ax.set_title(f"{title}: point density by distance from boundary")
    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"saved {out_path}")


if __name__ == "__main__":
    plot_points(SOL_64, 64, "n=64 baseline construction (C(64) >= 112)",
                os.path.join(FIGDIR, "baseline_n64.png"))
    plot_points(SOL_100, 100, "n=100 baseline construction (C(100) >= 164)",
                os.path.join(FIGDIR, "baseline_n100.png"))
    plot_ring_histogram(SOL_64, 64, "n=64 baseline",
                         os.path.join(FIGDIR, "ring_histogram_n64.png"))
    plot_ring_histogram(SOL_100, 100, "n=100 baseline",
                         os.path.join(FIGDIR, "ring_histogram_n100.png"))
