/* exact.c -- exhaustive maximum isosceles-free subset of an n x m integer grid.
 *
 * PROBLEM.  S subset of {0..W-1} x {0..H-1}.  Forbidden: three distinct
 * a,b,c in S with |ab| = |bc|.  Maximise |S|.
 *
 * ALL ARITHMETIC IS EXACT INTEGER (squared distances only).
 *
 * ALGORITHM.  Branch and bound / Tomita-style maximum-independent-set search
 * on the 3-uniform conflict hypergraph.
 *
 *   Key precomputation:  bad[p][s] = bitset of all q (q != p,s) such that
 *   {p,s,q} contains an isosceles triple.  This is SYMMETRIC in p,s, and it
 *   is all we need: if S is isosceles-free and we add v, the surviving
 *   candidates are exactly  P \ union_{s in S} bad[v][s].   (Every new
 *   forbidden triple must involve v and one earlier member of S; triples
 *   inside S were removed at earlier levels.)
 *
 *   Search:  expand(S,P):
 *       while P nonempty:
 *          if |S| + bound(P) <= best: return          (whole loop pruned)
 *          v = highest-index vertex of P;  P := P \ {v}
 *          expand(S+{v}, P & ~conflict(v))
 *
 *   This enumerates every maximal set: at each level we either take v or
 *   permanently drop it, and dropping is only done after fully exploring the
 *   take-branch.  Hence EXHAUSTIVE up to the (sound) bound pruning.
 *
 *   bound(P):  for any s in S, S+{s} isosceles-free means at most one point
 *   of the final answer sits at any given squared distance from s.  So
 *   |final cap P| <= #{distinct squared distances from s to P}.  We take the
 *   minimum over s in S (a "shell partition" = clique cover bound).
 *   Optionally we refine it with a greedy clique cover on the pairwise
 *   conflict graph induced on P.
 *
 *   Symmetry: the minimum-index point of S is restricted to a fundamental
 *   domain of the symmetry group of the board (D4 for squares, Klein 4-group
 *   for proper rectangles).  Sound because every orbit contains a
 *   lexicographically minimal representative, whose min-index point m
 *   satisfies idx(m) <= idx(g(m)) for all g in the group.
 *
 * USAGE: exact W H [lowerbound] [threads]
 *   Prints the optimum and one witness set.  If lowerbound L is given the
 *   search only looks for sets of size > L (still exhaustive as a proof that
 *   none exists, i.e. it certifies the upper bound L when it finds nothing).
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

static int W, H, N, NW;            /* board width/height, #points, #words */
static u64 *bad;                   /* N*N*NW  */
static int *dx2;                   /* dist2[p*N+q] */
static int DMAX;
static int best;
static int bestset[4096];
static long long nodes;

#define BADP(p,s) (bad + ((size_t)(p)*N + (s))*NW)

static inline int px(int i){ return i % W; }
static inline int py(int i){ return i / W; }

/* ---------------- bitset helpers ---------------- */
static inline int popcnt_arr(const u64 *a){
    int c=0; for(int i=0;i<NW;i++) c += __builtin_popcountll(a[i]); return c;
}
static inline int first_bit(const u64 *a){
    for(int i=0;i<NW;i++) if(a[i]) return i*64+__builtin_ctzll(a[i]);
    return -1;
}
static inline int last_bit(const u64 *a){
    for(int i=NW-1;i>=0;i--) if(a[i]) return i*64+63-__builtin_clzll(a[i]);
    return -1;
}

/* ---------------- precomputation ---------------- */
static void precompute(void){
    dx2 = malloc(sizeof(int)*(size_t)N*N);
    for(int p=0;p<N;p++) for(int q=0;q<N;q++){
        int ax=px(p),ay=py(p),bx=px(q),by=py(q);
        dx2[(size_t)p*N+q]=(ax-bx)*(ax-bx)+(ay-by)*(ay-by);
    }
    DMAX = (W-1)*(W-1)+(H-1)*(H-1);
    size_t sz = (size_t)N*N*NW;
    bad = calloc(sz,sizeof(u64));
    if(!bad){ fprintf(stderr,"OOM bad table (%zu words)\n",sz); exit(1);}
    /* bad[p][s] = { q : {p,s,q} contains an isosceles triple } */
    for(int p=0;p<N;p++){
        for(int s=p+1;s<N;s++){
            int dps = dx2[(size_t)p*N+s];
            u64 *bp = BADP(p,s), *bs = BADP(s,p);
            for(int q=0;q<N;q++){
                if(q==p||q==s) continue;
                int dpq = dx2[(size_t)p*N+q];
                int dsq = dx2[(size_t)s*N+q];
                if(dpq==dps || dsq==dps || dpq==dsq){
                    bp[q>>6] |= 1ULL<<(q&63);
                }
            }
            memcpy(bs,bp,sizeof(u64)*NW);
        }
    }
}

/* ---------------- bound ---------------- */
/* number of distinct squared distances from apex s to the vertices of P */
static int shellcount(int s, const u64 *P, unsigned char *mark, int stamp){
    const int *drow = dx2 + (size_t)s*N;
    int c=0;
    for(int w=0;w<NW;w++){
        u64 x=P[w];
        while(x){
            int q = w*64+__builtin_ctzll(x); x&=x-1;
            int r = drow[q];
            if(mark[r]!=stamp){ mark[r]=stamp; c++; }
        }
    }
    return c;
}

typedef struct {
    int Sarr[512];
    unsigned char *mark;
    int stamp;
    u64 *stack;        /* NW * (N+2) */
    int lbest;
    int lsetn;
    int lset[4096];
    long long lnodes;
} Ctx;

static void expand(Ctx *ctx, int depth, u64 *P)
{
    ctx->lnodes++;
    u64 *nextP = ctx->stack + (size_t)depth*NW;
    for(;;){
        int cnt = popcnt_arr(P);
        if(cnt==0) return;
        if(depth + cnt <= ctx->lbest) return;
        /* shell bound: min over recent apexes in S */
        int lim = depth<6 ? depth : 6;          /* use the 6 most recent */
        int bnd = cnt;
        for(int t=0;t<lim;t++){
            int s = ctx->Sarr[depth-1-t];
            ctx->stamp++;
            if(ctx->stamp>250){ memset(ctx->mark,0,DMAX+1); ctx->stamp=1; }
            int b = shellcount(s,P,ctx->mark,ctx->stamp);
            if(b<bnd) bnd=b;
            if(depth+bnd<=ctx->lbest) return;
        }
        int v = last_bit(P);
        P[v>>6] &= ~(1ULL<<(v&63));
        /* build child candidate set */
        memcpy(nextP,P,sizeof(u64)*NW);
        for(int t=0;t<depth;t++){
            const u64 *b = BADP(v,ctx->Sarr[t]);
            for(int w=0;w<NW;w++) nextP[w] &= ~b[w];
        }
        ctx->Sarr[depth]=v;
        if(depth+1 > ctx->lbest){
            ctx->lbest = depth+1;
            ctx->lsetn = depth+1;
            memcpy(ctx->lset,ctx->Sarr,sizeof(int)*(depth+1));
        }
        expand(ctx,depth+1,nextP);
    }
}

/* fundamental domain of the board's symmetry group under index order */
static int in_fund(int p){
    int x=px(p), y=py(p);
    int bi = y*W+x, cand;
    int xs[8],ys[8],k=0;
    xs[k]=x; ys[k]=y; k++;
    xs[k]=W-1-x; ys[k]=y; k++;
    xs[k]=x; ys[k]=H-1-y; k++;
    xs[k]=W-1-x; ys[k]=H-1-y; k++;
    if(W==H){
        xs[k]=y; ys[k]=x; k++;
        xs[k]=H-1-y; ys[k]=x; k++;
        xs[k]=y; ys[k]=W-1-x; k++;
        xs[k]=H-1-y; ys[k]=W-1-x; k++;
    }
    for(int i=0;i<k;i++){ cand = ys[i]*W+xs[i]; if(cand<bi) return 0; }
    return 1;
}

int main(int argc,char**argv){
    W = atoi(argv[1]); H = argc>2?atoi(argv[2]):W;
    int lb = argc>3?atoi(argv[3]):0;
    int nthreads = argc>4?atoi(argv[4]):1;
    N = W*H; NW = (N+63)/64;
    precompute();
    best = lb;
    int nbest=0;
    clock_t t0=clock();

    /* root split: choose the minimum-index point v0 of S (in fundamental
     * domain); all points < v0 are excluded from the candidate set. */
    int roots[4096],nr=0;
    for(int v=0;v<N;v++) if(in_fund(v)) roots[nr++]=v;

    long long tot_nodes=0;
#ifdef _OPENMP
    omp_set_num_threads(nthreads);
#endif
#pragma omp parallel
    {
        Ctx *ctx = malloc(sizeof(Ctx));
        ctx->mark = calloc(DMAX+2,1);
        ctx->stamp = 0;
        ctx->stack = malloc(sizeof(u64)*(size_t)NW*(N+2));
        ctx->lbest = lb; ctx->lnodes=0; ctx->lsetn=0;
        u64 *P0 = malloc(sizeof(u64)*NW);
#pragma omp for schedule(dynamic,1)
        for(int r=0;r<nr;r++){
            int v0=roots[r];
#pragma omp critical
            { if(best>ctx->lbest) ctx->lbest=best; }
            memset(P0,0,sizeof(u64)*NW);
            for(int q=v0+1;q<N;q++) P0[q>>6]|=1ULL<<(q&63);
            ctx->Sarr[0]=v0;
            if(1>ctx->lbest){ ctx->lbest=1; ctx->lsetn=1; ctx->lset[0]=v0; }
            expand(ctx,1,P0);
#pragma omp critical
            {
                if(ctx->lbest>best && ctx->lsetn==ctx->lbest){ best=ctx->lbest; nbest=best;
                    memcpy(bestset,ctx->lset,sizeof(int)*best); }
            }
        }
#pragma omp critical
        { tot_nodes += ctx->lnodes; }
    }
    nodes=tot_nodes;
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    printf("BOARD %dx%d  OPT %d  nodes %lld  time %.2fs\n",W,H,best,nodes,el);
    if(nbest){
        printf("SET");
        for(int i=0;i<best;i++) printf(" %d,%d",px(bestset[i]),py(bestset[i]));
        printf("\n");
    }
    return 0;
}
