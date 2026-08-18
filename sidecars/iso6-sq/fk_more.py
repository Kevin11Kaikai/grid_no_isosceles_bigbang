"""F_3(n) for n=8,9 only."""
from itertools import combinations

from fk import F_k


def main():
    for n in (8, 9):
        f3, ys = F_k(n, 3)
        print(
            {
                "n": n,
                "F_2": 2 * n - 2,
                "F_3": f3,
                "rows": list(ys),
                "Q_SQ": {8: 17, 9: 20}[n],
            },
            flush=True,
        )


if __name__ == "__main__":
    main()
