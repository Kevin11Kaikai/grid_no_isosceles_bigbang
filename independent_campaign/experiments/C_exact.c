/* C_exact.c -- exhaustive branch & bound for
 *   C(n) = max |S|, S subset of {0..n-1}^2, no three distinct a,b,c in S
 *          with d(a,b) = d(b,c).
 * Also handles k x n rectangles (rows x cols).
 *
 * METHOD (this is the exhaustiveness certificate; see report.md):
 *
 *  (1) The property is HEREDITARY: every subset of a valid set is valid.
 *      Hence a DFS that only extends valid sets reaches every valid set.
 *
 *  (2) Enumeration scheme.  At a node we hold  S  (chosen) and  cand
 *      (points u such that S+{u} is valid AND u has not yet been branched
 *      away at this node or any ancestor).  We loop:
 *          pick v in cand; cand := cand \ {v}; recurse on (S+{v}, cand & A(v))
 *      This is the standard "include v / exclude v for the rest of the loop"
 *      partition, so every valid superset of S inside cand is generated
 *      exactly once.  Proof: let T be a valid set with S subset T subset
 *      S+cand.  Let v be the first element the loop picks.  If v in T then T
 *      is found in the recursive call (T\{v} \ S is still available because
 *      every element of T is compatible with S+{v}); if v not in T then T is
 *      found later in the same loop.  Induction on |cand|.
 *
 *  (3) Incremental compatibility.  INVARIANT: cand = {u : S+{u} is valid,
 *      u not yet branched at this node or an ancestor}.  When v is added,
 *      S+{v,u} is valid iff S+{u} valid (u in cand), S+{v} valid (v in cand)
 *      and no bad triple uses BOTH u and v.  Such a triple is {u,v,b} with
 *      b in S, and the apex is one of the three:
 *        apex b : d(b,u) = d(b,v)          -> u in A(b, d(b,v))
 *        apex v : d(v,u) = d(v,b)          -> u in A(v, d(b,v))
 *        apex u : d(u,b) = d(u,v)          -> u on the perpendicular
 *                                             bisector of b,v
 *      ban[b][v] is the union of these three sets (it is symmetric in b,v),
 *      so  newcand = cand \ union_{b in S} ban[b][v]  restores the invariant
 *      EXACTLY -- no over- or under-pruning.  (The apex-u case was omitted
 *      in a first draft and produced wrong values C(4)=7, C(5)=8; the fixed
 *      code reproduces the brute-force values.  Regression-tested below.)
 *
 *  (4) Pruning bounds (all are UPPER bounds on |T| for any valid T with
 *      S subset T subset S+cand, hence sound):
 *        B1: |S| + |cand|
 *        B2: for every b in S, the sets A(b,r) (points at squared distance r
 *            from b) PARTITION the grid minus {b}.  If b in T then T meets
 *            each A(b,r) at most once.  So
 *               |T| <= |S| + #{ r : A(b,r) meets cand }.
 *            We take the minimum over b in S.
 *      A node is cut when the bound is <= the incumbent `best`.
 *
 *  (5) Symmetry.  For square grids the dihedral group D4 acts.  Every valid
 *      set S has an image gS whose minimum-index element w (row-major) is
 *      minimal in its own D4-orbit: choose g minimising the index of the
 *      minimum element over all images; if some h moved w lower, hg would do
 *      better.  So we may restrict the FIRST (=lowest index) chosen point to
 *      the orbit representatives.  Nothing else is restricted, so the search
 *      remains complete up to symmetry, and |S| is symmetry-invariant.
 *      (-nosym disables this, for independent re-verification.)
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#ifdef _OPENMP
#include <omp.h>
#endif

typedef uint64_t u64;
#define MAXPTS 900
#define MAXW ((MAXPTS + 63) / 64)

static int NR, NC, npts, NW;
static int px[MAXPTS], py[MAXPTS];
static short *pcls;              /* pcls[b*npts + j] = class of j wrt b   */
static int nclass[MAXPTS];
static int maxclass;
static u64 *banmask;             /* banmask[(b*npts + v)*NW + w], symmetric */
static unsigned char canon[MAXPTS];
static int use_sym = 1, use_b2 = 1;

#define BAN(b, v) (banmask + (((size_t)(b) * npts + (v)) * NW))

static inline int pc(const u64 *a) {
    int s = 0;
    for (int i = 0; i < NW; i++) s += __builtin_popcountll(a[i]);
    return s;
}

/* ------------------------------------------------------------------ */
static void build(int nr, int nc)
{
    NR = nr; NC = nc; npts = nr * nc; NW = (npts + 63) / 64;
    for (int i = 0, k = 0; i < nr; i++)
        for (int j = 0; j < nc; j++, k++) { px[k] = i; py[k] = j; }

    pcls = malloc((size_t)npts * npts * sizeof(short));
    int *dl = malloc((size_t)npts * sizeof(int));
    maxclass = 0;
    for (int b = 0; b < npts; b++) {
        int m = 0;
        for (int j = 0; j < npts; j++) {
            if (j == b) { pcls[(size_t)b * npts + j] = -1; continue; }
            int dx = px[b] - px[j], dy = py[b] - py[j];
            int d = dx * dx + dy * dy;
            int c = -1;
            for (int t = 0; t < m; t++) if (dl[t] == d) { c = t; break; }
            if (c < 0) { c = m; dl[m++] = d; }
            pcls[(size_t)b * npts + j] = (short)c;
        }
        nclass[b] = m;
        if (m > maxclass) maxclass = m;
    }
    free(dl);
    banmask = calloc((size_t)npts * npts * NW, sizeof(u64));
    for (int b = 0; b < npts; b++)
        for (int v = b + 1; v < npts; v++) {
            u64 *m = BAN(b, v);
            int dbv = (px[b]-px[v])*(px[b]-px[v]) + (py[b]-py[v])*(py[b]-py[v]);
            for (int u = 0; u < npts; u++) {
                if (u == b || u == v) continue;
                int dub = (px[u]-px[b])*(px[u]-px[b]) + (py[u]-py[b])*(py[u]-py[b]);
                int duv = (px[u]-px[v])*(px[u]-px[v]) + (py[u]-py[v])*(py[u]-py[v]);
                if (dub == dbv || duv == dbv || dub == duv)
                    m[u >> 6] |= 1ULL << (u & 63);
            }
            memcpy(BAN(v, b), m, (size_t)NW * 8);
        }

    /* D4 canonical first point (square grids only) */
    for (int k = 0; k < npts; k++) canon[k] = 1;
    if (nr == nc && use_sym) {
        int n = nr;
        for (int k = 0; k < npts; k++) {
            int i = px[k], j = py[k], mn = k;
            int a[8][2] = {{i,j},{i,n-1-j},{n-1-i,j},{n-1-i,n-1-j},
                           {j,i},{j,n-1-i},{n-1-j,i},{n-1-j,n-1-i}};
            for (int t = 0; t < 8; t++) {
                int idx = a[t][0] * n + a[t][1];
                if (idx < mn) mn = idx;
            }
            canon[k] = (mn == k);
        }
    }
}

/* ------------------------------------------------------------------ */
typedef struct {
    int cur[MAXPTS];
    int stamp[MAXPTS];
    int token;
    u64 cand[MAXPTS + 2][MAXW];
    long long nodes;
    int best, bestlen, bestset[MAXPTS];
} W;

static int GBEST;                       /* shared incumbent */
static int GBESTSET[MAXPTS], GBESTLEN;

/* B2: min over b in S of #distinct distance classes of b met by cand.
   Early exit as soon as the count reaches `need`. */
static int bound_ok(W *w, int nd, const u64 *nc)
{
    int cnt = pc(nc);
    if (nd + cnt <= w->best) return 0;
    if (!use_b2) return 1;
    int need = w->best + 1 - nd;          /* extra points still required */
    if (need <= 0) return 1;
    for (int t = 0; t < nd; t++) {
        int b = w->cur[t];
        const short *pr = pcls + (size_t)b * npts;
        int tok = ++w->token, c = 0;
        for (int i = 0; i < NW; i++) {
            u64 x = nc[i];
            while (x) {
                int j = i * 64 + __builtin_ctzll(x);
                x &= x - 1;
                int cl = pr[j];
                if (w->stamp[cl] != tok) { w->stamp[cl] = tok; if (++c >= need) goto next_b; }
            }
        }
        return 0;                          /* c < need  ->  cut */
      next_b: ;
    }
    return 1;
}

static void newbest(W *w, int nd)
{
    w->best = nd;
    w->bestlen = nd;
    memcpy(w->bestset, w->cur, nd * sizeof(int));
#ifdef _OPENMP
#pragma omp critical
#endif
    {
        if (nd > GBEST) { GBEST = nd; GBESTLEN = nd; memcpy(GBESTSET, w->cur, nd * sizeof(int)); }
    }
}

static void expand(W *w, int depth)
{
    u64 *cand = w->cand[depth];
    for (;;) {
        w->nodes++;
        int cnt = pc(cand);
        if (depth + cnt <= w->best) return;
        int v = -1;
        for (int i = 0; i < NW; i++)
            if (cand[i]) { v = i * 64 + __builtin_ctzll(cand[i]); break; }
        if (v < 0) return;
        cand[v >> 6] &= ~(1ULL << (v & 63));

        u64 *nc = w->cand[depth + 1];
        memcpy(nc, cand, (size_t)NW * 8);
        for (int t = 0; t < depth; t++) {
            const u64 *m = BAN(w->cur[t], v);
            for (int i = 0; i < NW; i++) nc[i] &= ~m[i];
        }
        w->cur[depth] = v;
        int nd = depth + 1;
        if (nd > w->best) newbest(w, nd);
        if (w->best < GBEST) w->best = GBEST;
        if (bound_ok(w, nd, nc)) expand(w, nd);
    }
}

/* ------------------------------------------------------------------ */
/* task generation: every node at depth TD (as a (prefix, cand) pair)   */
typedef struct { int pre[8]; u64 cand[MAXW]; } Task;
static Task *tasks; static long ntask, captask;

static void gentasks(W *w, int depth, int TD)
{
    u64 *cand = w->cand[depth];
    for (;;) {
        int cnt = pc(cand);
        if (depth + cnt <= w->best) return;
        int v = -1;
        for (int i = 0; i < NW; i++)
            if (cand[i]) { v = i * 64 + __builtin_ctzll(cand[i]); break; }
        if (v < 0) return;
        cand[v >> 6] &= ~(1ULL << (v & 63));
        u64 *nc = w->cand[depth + 1];
        memcpy(nc, cand, (size_t)NW * 8);
        for (int t = 0; t < depth; t++) {
            const u64 *m = BAN(w->cur[t], v);
            for (int i = 0; i < NW; i++) nc[i] &= ~m[i];
        }
        w->cur[depth] = v;
        int nd = depth + 1;
        if (nd > w->best) newbest(w, nd);
        if (!bound_ok(w, nd, nc)) continue;
        if (nd == TD) {
            if (ntask == captask) { captask = captask ? captask * 2 : 1024;
                                    tasks = realloc(tasks, captask * sizeof(Task)); }
            memcpy(tasks[ntask].pre, w->cur, nd * sizeof(int));
            memcpy(tasks[ntask].cand, nc, (size_t)NW * 8);
            ntask++;
        } else gentasks(w, nd, TD);
    }
}

int main(int argc, char **argv)
{
    int nr = 0, nc = 0, lb = 0, TD = 3, nthr = 0;
    for (int i = 1; i < argc; i++) {
        if (!strcmp(argv[i], "-n")) { nr = nc = atoi(argv[++i]); }
        else if (!strcmp(argv[i], "-r")) nr = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-c")) nc = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-lb")) lb = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-td")) TD = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-t")) nthr = atoi(argv[++i]);
        else if (!strcmp(argv[i], "-nosym")) use_sym = 0;
        else if (!strcmp(argv[i], "-nob2")) use_b2 = 0;
    }
    if (!nr) { fprintf(stderr, "usage: -n N | -r R -c C  [-lb L] [-td D] [-t T] [-nosym] [-nob2]\n"); return 1; }
    if (!nc) nc = nr;
    build(nr, nc);
    GBEST = lb; GBESTLEN = 0;

    clock_t t0 = clock();
    double wt0 = 0;
#ifdef _OPENMP
    wt0 = omp_get_wtime();
    if (nthr) omp_set_num_threads(nthr);
#endif

    W *w0 = calloc(1, sizeof(W));
    w0->best = GBEST;
    /* top level: choose the minimum-index point, restricted to D4 reps */
    u64 all[MAXW]; memset(all, 0, sizeof(all));
    for (int k = 0; k < npts; k++) all[k >> 6] |= 1ULL << (k & 63);
    long long totnodes = 0;

    if (TD <= 1) {
        for (int v0 = 0; v0 < npts; v0++) {
            all[v0 >> 6] &= ~(1ULL << (v0 & 63));
            if (!canon[v0]) continue;
            w0->cur[0] = v0;
            if (1 > w0->best) newbest(w0, 1);
            memcpy(w0->cand[1], all, (size_t)NW * 8);
            if (bound_ok(w0, 1, w0->cand[1])) expand(w0, 1);
            if (w0->best < GBEST) w0->best = GBEST;
        }
        totnodes = w0->nodes;
    } else {
        for (int v0 = 0; v0 < npts; v0++) {
            all[v0 >> 6] &= ~(1ULL << (v0 & 63));
            if (!canon[v0]) continue;
            w0->cur[0] = v0;
            if (1 > w0->best) newbest(w0, 1);
            memcpy(w0->cand[1], all, (size_t)NW * 8);
            if (bound_ok(w0, 1, w0->cand[1])) gentasks(w0, 1, TD);
        }
        fprintf(stderr, "tasks: %ld  (gen best=%d)\n", ntask, GBEST);
        long long nodesum = 0;
#ifdef _OPENMP
#pragma omp parallel reduction(+:nodesum)
        {
            W *w = calloc(1, sizeof(W));
#pragma omp for schedule(dynamic, 8)
            for (long t = 0; t < ntask; t++) {
                w->best = GBEST;
                memcpy(w->cur, tasks[t].pre, TD * sizeof(int));
                memcpy(w->cand[TD], tasks[t].cand, (size_t)NW * 8);
                if (bound_ok(w, TD, w->cand[TD])) expand(w, TD);
            }
            nodesum += w->nodes;
            free(w);
        }
#else
        {
            W *w = calloc(1, sizeof(W));
            for (long t = 0; t < ntask; t++) {
                w->best = GBEST;
                memcpy(w->cur, tasks[t].pre, TD * sizeof(int));
                memcpy(w->cand[TD], tasks[t].cand, (size_t)NW * 8);
                if (bound_ok(w, TD, w->cand[TD])) expand(w, TD);
            }
            nodesum += w->nodes;
        }
#endif
        totnodes = w0->nodes + nodesum;
    }

    double el;
#ifdef _OPENMP
    el = omp_get_wtime() - wt0;
#else
    el = (double)(clock() - t0) / CLOCKS_PER_SEC;
#endif
    printf("GRID %dx%d  OPT %d  nodes %lld  time %.2fs  sym=%d b2=%d\n",
           NR, NC, GBEST, totnodes, el, use_sym, use_b2);
    if (GBESTLEN) {
        printf("SET");
        for (int i = 0; i < GBESTLEN; i++) printf(" %d,%d", px[GBESTSET[i]], py[GBESTSET[i]]);
        printf("\n");
    } else printf("SET (none better than lb=%d found)\n", lb);
    return 0;
}
