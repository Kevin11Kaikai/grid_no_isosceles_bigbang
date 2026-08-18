/* Route C -- METHOD A
 * Exhaustive maximum-independent-set search in the 3-uniform "isosceles" hypergraph
 * on an R x Cc grid.
 *
 * State invariant: every cell in the candidate bitset `cand` is INDIVIDUALLY addable
 * to the current partial set S (i.e. S+{u} is still valid).  When we add v, the new
 * candidate set is obtained with pure bitmask ANDs:
 *
 *   for each b in S:
 *       ch &= ~circle[b][ d(b,v) ]   // apex b: no other point may sit at distance d(b,v) from b
 *       ch &= ~circle[v][ d(v,b) ]   // apex v: no other point may sit at distance d(v,b) from v
 *       ch &= ~bisect[v][b]          // apex u: u must not be equidistant from v and b
 *
 * plus ch &= {cells of index > idx(v)} (enforced by the increasing-order loop).
 * These three families are exactly the conditions that can newly fail, so the
 * invariant is maintained and NOTHING addable is dropped.
 *
 * Bound: |S| + popcount(cand) <= best  ==>  prune (cand is a superset of any
 * completion, so this is a valid upper bound on what the subtree can reach).
 *
 * Symmetry (root only, optional):
 *   - the smallest-index point of S is restricted to cells that are minimal in their
 *     orbit under the board's symmetry group;
 *   - the second-smallest point u is restricted by idx(u) <= idx(g(u)) for all g in
 *     the stabiliser of the first point.
 *   Both are sound (see report.md for the proof).
 *
 * usage: solveA R C [initial_best] [--nosym] [--task v0 v1]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>

#ifndef NWC
#define NWC 4
#endif
typedef uint64_t u64;

static int R, Cc, N, MAXD, NW;
static u64 *circ;           /* circ[(a*(MAXD+1)+d)*NWC] */
static u64 *bis;            /* bis[(a*N+b)*NWC]          */
static int *dst;            /* dst[a*N+b] squared distance */
static int best = 0;
static int S[600], bestset[600], bestn = 0;
static long long nodes = 0;
static int usesym = 1;
static int taskv0 = -1, taskv1 = -1;

#define XOF(i) ((i)/Cc)
#define YOF(i) ((i)%Cc)

static inline int pc(const u64 *a){int s=0;for(int i=0;i<NWC;i++)s+=__builtin_popcountll(a[i]);return s;}
static inline void bset(u64*a,int i){a[i>>6]|=1ULL<<(i&63);}
static inline int bget(const u64*a,int i){return (a[i>>6]>>(i&63))&1ULL;}

static void report(double t){
    printf("BEST %d  nodes %lld  t %.2f  SET", best, nodes, t);
    for(int i=0;i<bestn;i++) printf(" %d,%d", XOF(bestset[i]), YOF(bestset[i]));
    printf("\n"); fflush(stdout);
}

static double now(void){ return (double)clock()/CLOCKS_PER_SEC; }

static void dfs(int depth, u64 *cand){
    nodes++;
    int cnt = pc(cand);
    if (depth + cnt <= best) return;
    if (depth > best){ best = depth; bestn = depth; memcpy(bestset,S,depth*sizeof(int)); report(now()); }
    u64 loc[NWC]; memcpy(loc,cand,sizeof(loc));
    for(;;){
        int v = -1;
        for(int w=0; w<NWC; w++) if(loc[w]){ v = w*64 + __builtin_ctzll(loc[w]); break; }
        if (v < 0) break;
        loc[v>>6] &= ~(1ULL<<(v&63));
        if (depth + 1 + pc(loc) <= best) break;   /* loc only shrinks -> all later branches also bounded */
        u64 ch[NWC]; memcpy(ch,loc,sizeof(ch));
        const int *dv = dst + (size_t)v*N;
        for(int i=0;i<depth;i++){
            int b = S[i];
            int d = dv[b];
            const u64 *m1 = circ + ((size_t)b*(MAXD+1)+d)*NWC;
            const u64 *m2 = circ + ((size_t)v*(MAXD+1)+d)*NWC;
            const u64 *m3 = bis  + ((size_t)v*N+b)*NWC;
            for(int w=0;w<NWC;w++) ch[w] &= ~(m1[w]|m2[w]|m3[w]);
        }
        S[depth]=v;
        dfs(depth+1, ch);
    }
}

/* ---- symmetry ---- */
static int NG; static int gmap[8][600];
static void buildgroup(void){
    NG=0;
    int flips = (R==Cc) ? 8 : 4;
    for(int g=0; g<flips; g++){
        for(int i=0;i<N;i++){
            int x=XOF(i), y=YOF(i);
            if(g&1) x = R-1-x;
            if(g&2) y = Cc-1-y;
            if(g&4){ int t=x; x=y; y=t; }
            gmap[NG][i] = x*Cc+y;
        }
        NG++;
    }
}

int main(int argc,char**argv){
    R = atoi(argv[1]); Cc = atoi(argv[2]);
    if(argc>3) best = atoi(argv[3]);
    for(int i=4;i<argc;i++){
        if(!strcmp(argv[i],"--nosym")) usesym=0;
        else if(!strcmp(argv[i],"--task")){ taskv0=atoi(argv[i+1]); taskv1=atoi(argv[i+2]); i+=2; }
    }
    N = R*Cc;
    if(N > NWC*64){ fprintf(stderr,"N=%d too big for NWC=%d\n",N,NWC); return 1; }
    MAXD = (R-1)*(R-1)+(Cc-1)*(Cc-1);
    NW = NWC;
    dst = malloc((size_t)N*N*sizeof(int));
    circ = calloc((size_t)N*(MAXD+1)*NWC, sizeof(u64));
    bis  = calloc((size_t)N*N*NWC, sizeof(u64));
    if(!dst||!circ||!bis){ fprintf(stderr,"alloc fail\n"); return 1; }
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){
        int dx=XOF(a)-XOF(b), dy=YOF(a)-YOF(b);
        int d=dx*dx+dy*dy;
        dst[(size_t)a*N+b]=d;
        if(a!=b) bset(circ + ((size_t)a*(MAXD+1)+d)*NWC, b);
    }
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){
        u64 *m = bis + ((size_t)a*N+b)*NWC;
        for(int u=0;u<N;u++) if(dst[(size_t)u*N+a]==dst[(size_t)u*N+b]) bset(m,u);
    }
    buildgroup();

    if(N>=1 && best<1){ best=1; bestn=1; bestset[0]=0; }

    double t0 = now();
    /* root: choose first (minimum-index) point */
    for(int v0=0; v0<N; v0++){
        if(usesym){ int mn=v0; for(int g=0;g<NG;g++) if(gmap[g][v0]<mn) mn=gmap[g][v0];
                    if(mn!=v0) continue; }
        if(taskv0>=0 && v0!=taskv0) continue;
        /* stabiliser mask for the 2nd point */
        u64 stab[NWC]; for(int w=0;w<NWC;w++) stab[w]=~0ULL;
        if(usesym){
            for(int w=0;w<NWC;w++) stab[w]=0;
            for(int u=0;u<N;u++){
                int ok=1;
                for(int g=0;g<NG;g++){ if(gmap[g][v0]==v0 && gmap[g][u]<u){ ok=0; break; } }
                if(ok) bset(stab,u);
            }
        }
        for(int v1=v0+1; v1<N; v1++){
            if(!bget(stab,v1)) continue;
            if(taskv1>=0 && v1!=taskv1) continue;
            if(2 + (N-1-v1) <= best) break;
            u64 ch[NWC]; memset(ch,0,sizeof(ch));
            for(int u=v1+1;u<N;u++) bset(ch,u);
            /* filter w.r.t. S={v0,v1} : only pair (b=v0, v=v1) matters */
            int d = dst[(size_t)v1*N+v0];
            const u64 *m1 = circ + ((size_t)v0*(MAXD+1)+d)*NWC;
            const u64 *m2 = circ + ((size_t)v1*(MAXD+1)+d)*NWC;
            const u64 *m3 = bis  + ((size_t)v1*N+v0)*NWC;
            for(int w=0;w<NWC;w++) ch[w] &= ~(m1[w]|m2[w]|m3[w]);
            S[0]=v0; S[1]=v1;
            if(2 > best){ best=2; bestn=2; memcpy(bestset,S,2*sizeof(int)); }
            dfs(2, ch);
        }
    }
    printf("DONE grid %dx%d  OPT %d  nodes %lld  time %.2f  sym=%d\n", R,Cc,best,nodes,now()-t0,usesym);
    printf("SET"); for(int i=0;i<bestn;i++) printf(" %d,%d", XOF(bestset[i]), YOF(bestset[i])); printf("\n");
    return 0;
}
