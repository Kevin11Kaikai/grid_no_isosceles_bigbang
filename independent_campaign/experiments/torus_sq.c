/* g(q) = max square-corner-free subset of the torus (Z_q)^2, exhaustive.
 *
 * A square corner is {b, u, v} with v = b + i*(u-b), u != b, i*(x,y) = (-y,x).
 * For an unordered pair {a,b} the cells x completing a corner are exactly four:
 *    t(a,b) = a + i*(b-a)              (apex a)
 *    t(b,a) = b + i*(a-b)              (apex b)
 *    x with t(x,a) = b, i.e. x = (1-i)^{-1}(b - i a)     (apex x, legs a,b)
 *    x with t(x,b) = a, i.e. x = (1-i)^{-1}(a - i b)
 * (1-i) is the matrix [[1,1],[-1,1]], det 2, so it is invertible mod odd q; for even q
 * the last two cells are computed by an explicit table search instead.
 *
 * DFS over cells in increasing index order carrying a candidate bitset with the
 * invariant "every candidate is individually addable to S and has a larger index".
 * Bound: |S| + popcount(cand) <= best  =>  prune.  Translation invariance on the torus
 * lets us fix cell (0,0) in S without loss.
 *
 * usage: torus_sq q [start_best]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define WMAX 8                      /* 8*64 = 512 bits, enough for q <= 22 */
static int Q, N, NW;

typedef struct { uint64_t w[WMAX]; } BS;

static int  third[512][512];        /* third[b][u] = b + i*(u-b) */
static int  fourcell[512][512][8];  /* the <=6 completions of the pair {a,b} */
static int  nfour[512][512];
static int  pairbad[512][512];      /* {a,x} alone already infeasible (even q only) */

static inline int idx(int x, int y) { x %= Q; if (x < 0) x += Q; y %= Q; if (y < 0) y += Q; return x * Q + y; }

static inline void bs_clear(BS *a)              { memset(a->w, 0, sizeof(a->w)); }
static inline void bs_set(BS *a, int i)         { a->w[i >> 6] |= 1ULL << (i & 63); }
static inline int  bs_get(const BS *a, int i)   { return (a->w[i >> 6] >> (i & 63)) & 1ULL; }
static inline void bs_unset(BS *a, int i)       { a->w[i >> 6] &= ~(1ULL << (i & 63)); }
static inline int  bs_count(const BS *a) {
    int c = 0; for (int k = 0; k < NW; k++) c += __builtin_popcountll(a->w[k]); return c;
}

static long long nodes = 0;
static int best = 0, bestset[512], curset[512];

static void rec(int depth, BS cand)
{
    nodes++;
    if (depth > best) { best = depth; memcpy(bestset, curset, sizeof(int) * depth); bestset[depth] = -1;
                        printf("   .. new best %d\n", best); fflush(stdout); }
    int rem = bs_count(&cand);
    if (depth + rem <= best) return;

    for (int p = 0; p < N; p++) {
        if (!bs_get(&cand, p)) continue;
        /* remaining candidates from p on */
        if (depth + rem <= best) return;
        rem--;                                  /* p is consumed by this branch */
        BS nc = cand;
        for (int j = 0; j <= p; j++) bs_unset(&nc, j);   /* increasing index order */
        /* filter: kill everything that would complete a corner with p and some s in S */
        for (int x = 0; x < N; x++) if (pairbad[p][x]) bs_unset(&nc, x);
        for (int s = 0; s < depth; s++) {
            int a = curset[s];
            for (int k = 0; k < nfour[a][p]; k++) bs_unset(&nc, fourcell[a][p][k]);
        }
        curset[depth] = p;
        rec(depth + 1, nc);
    }
}

int main(int argc, char **argv)
{
    Q = atoi(argv[1]);
    N = Q * Q;
    NW = (N + 63) / 64;
    if (NW > WMAX) { printf("q too large\n"); return 1; }
    if (argc > 2) best = atoi(argv[2]);

    for (int bx = 0; bx < Q; bx++) for (int by = 0; by < Q; by++)
    for (int ux = 0; ux < Q; ux++) for (int uy = 0; uy < Q; uy++) {
        int wx = ux - bx, wy = uy - by;
        third[idx(bx,by)][idx(ux,uy)] = idx(bx - wy, by + wx);
    }
    /* fourcell: for the pair (a,b), all x with {a,b,x} a square corner */
    for (int a = 0; a < N; a++) for (int b = 0; b < N; b++) {
        if (a == b) { nfour[a][b] = 0; continue; }
        /* x completes the pair {a,b} iff SOME ordered pair (p,r) drawn from the three
         * cells has third[p][r] equal to the remaining cell.  All six are checked. */
        int m = 0;
        for (int x = 0; x < N; x++) {
            if (x == a || x == b) continue;
            if (third[a][b] == x || third[b][a] == x ||
                third[a][x] == b || third[x][a] == b ||
                third[b][x] == a || third[x][b] == a) {
                if (m < 8) fourcell[a][b][m++] = x;
            }
        }
        nfour[a][b] = m;
    }
    /* pair-level infeasibility: an ordered pair (a,x), a != x, whose forbidden third
     * cell IS x itself.  Only possible when (1-i) is a zero divisor, i.e. q even. */
    for (int a = 0; a < N; a++) for (int x = 0; x < N; x++) {
        pairbad[a][x] = (a != x) && (third[a][x] == x || third[x][a] == a ||
                                     third[a][x] == a || third[x][a] == x);
    }

    /* Symmetry.  The defining equation v = i*u + (1-i)*b is Z[i]-linear, so every map
     * z -> alpha*z + beta with alpha a unit of Z_q[i], and complex conjugation, sends
     * square-corner-free sets to square-corner-free sets.  Translations let us put
     * 0 in S; then (lex-min argument) the second element may be assumed minimal in its
     * orbit under Stab(0) = units together with conjugation. */
    int orbmin[512]; memset(orbmin, 0, sizeof(orbmin));
    int nunit = 0;
    for (int d = 1; d < N; d++) {
        int dx = d / Q, dy = d % Q, mn = d;
        for (int ax = 0; ax < Q; ax++) for (int ay = 0; ay < Q; ay++) {
            int nrm = (ax * ax + ay * ay) % Q, inv = 0;
            for (int t = 1; t < Q; t++) if (nrm * t % Q == 1) inv = 1;
            if (!inv) continue;                       /* alpha must be a unit */
            if (d == 1) nunit++;
            /* alpha * z  and  alpha * conj(z) */
            int m1 = idx(ax * dx - ay * dy, ax * dy + ay * dx);
            int m2 = idx(ax * dx + ay * dy, -ax * dy + ay * dx);
            if (m1 && m1 < mn) mn = m1;
            if (m2 && m2 < mn) mn = m2;
        }
        orbmin[d] = (mn == d);
    }
    int nroot = 0; for (int d = 1; d < N; d++) nroot += orbmin[d];
    printf("q=%d: %d units, %d orbit-minimal second points (of %d)\n",
           Q, nunit, nroot, N - 1);

    BS cand; bs_clear(&cand);
    for (int p = 1; p < N; p++) bs_set(&cand, p);
    for (int x = 0; x < N; x++) if (pairbad[0][x]) bs_unset(&cand, x);
    curset[0] = 0;
    if (getenv("NOSYM")) {
        rec(1, cand);
    } else {
        best = best > 1 ? best : 1;
        for (int d = 1; d < N; d++) {
            if (!orbmin[d] || !bs_get(&cand, d)) continue;
            BS nc = cand;
            for (int x = 0; x <= d; x++) bs_unset(&nc, x);
            for (int x = 0; x < N; x++) if (pairbad[d][x]) bs_unset(&nc, x);
            for (int k = 0; k < nfour[0][d]; k++) bs_unset(&nc, fourcell[0][d][k]);
            curset[0] = 0; curset[1] = d;
            rec(2, nc);
        }
    }

    printf("q=%d  g(q)=%d  nodes=%lld\n", Q, best, nodes);
    printf("witness:");
    for (int k = 0; k < best; k++) printf(" (%d,%d)", bestset[k] / Q, bestset[k] % Q);
    printf("\n");
    return 0;
}
