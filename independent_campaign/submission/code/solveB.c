/* Route C -- METHOD B  (independent second method)
 *
 * Deliberately different from Method A in every part that could hide a bug:
 *   - different cell ORDER: cells are relabelled along anti-diagonals (x+y, then x),
 *     so the search tree has a completely different shape;
 *   - different VALIDITY ORACLE: no precomputed circle/bisector masks.  A candidate is
 *     tested straight from the definition, by looking at the per-point table of already
 *     used squared distances and re-deriving the apex-u distinctness test from scratch;
 *   - different BOUND: besides |S|+|cand| it uses a row/column 3-term-AP capacity bound.
 *     (Two points in the same row with a third one midway between them are isosceles with
 *     the middle point as apex, so the column set of every row is 3-AP-free; same for
 *     columns.  g[M] = size of the largest 3-AP-free subset of the column mask M is
 *     precomputed for all 2^C masks, and  sum_r g[ rowS_r | rowCand_r ]  is an upper
 *     bound on the final size, as is the analogous column sum.)
 *   - NO symmetry reduction whatsoever.
 *
 * usage: solveB R C [initial_best]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>

#ifndef NWC
#define NWC 4
#endif
#define DW 8                 /* distance-bitmap words: supports squared distance < 512 */
typedef uint64_t u64;

static int R, Cc, N, MAXD;
static int *DD;              /* DD[a*N+b] squared distance, in RELABELLED ids */
static int px[600], py[600]; /* relabelled id -> coordinates */
static int *gcap;            /* gcap[mask] = max 3-AP-free subset size of column mask */
static volatile int best = 0;
static int bestset[600], bestn = 0;
static long long nodes = 0;

static __thread int S[600];
static __thread u64 used[600][DW];
static __thread long long tnodes = 0;

static inline int pc(const u64 *a){int s=0;for(int i=0;i<NWC;i++)s+=__builtin_popcountll(a[i]);return s;}
static inline void bset(u64*a,int i){a[i>>6]|=1ULL<<(i&63);}
static inline int bget(const u64*a,int i){return (int)((a[i>>6]>>(i&63))&1ULL);}

static double now(void){ return (double)clock()/CLOCKS_PER_SEC; }

/* ---- naive addability oracle, straight from the definition ---- */
static int addable(int u, int depth){
    const int *du = DD + (size_t)u*N;
    for(int i=0;i<depth;i++){
        int p = S[i];
        int d = du[p];
        if (used[p][d>>6] >> (d&63) & 1ULL) return 0;      /* apex p would repeat a distance */
    }
    u64 seen[DW]; memset(seen,0,sizeof(seen));
    for(int i=0;i<depth;i++){
        int d = du[S[i]];
        if (seen[d>>6] >> (d&63) & 1ULL) return 0;         /* apex u would repeat a distance */
        seen[d>>6] |= 1ULL<<(d&63);
    }
    return 1;
}

static void push(int v,int depth){
    memset(used[v],0,sizeof(used[v]));
    const int *dv = DD + (size_t)v*N;
    for(int i=0;i<depth;i++){
        int p=S[i]; int d=dv[p];
        used[p][d>>6] |= 1ULL<<(d&63);
        used[v][d>>6] |= 1ULL<<(d&63);
    }
    S[depth]=v;
}
static void pop(int v,int depth){
    const int *dv = DD + (size_t)v*N;
    for(int i=0;i<depth;i++){
        int p=S[i]; int d=dv[p];
        used[p][d>>6] &= ~(1ULL<<(d&63));
    }
}

/* ---- row/column 3-AP capacity bound ---- */
static int capbound(int depth, const u64 *cand){
    int rs[32], cs[32], rc[32], cc2[32];
    for(int i=0;i<R;i++){ rs[i]=0; rc[i]=0; }
    for(int j=0;j<Cc;j++){ cs[j]=0; cc2[j]=0; }
    for(int i=0;i<depth;i++){ int v=S[i]; rs[px[v]] |= 1<<py[v]; cs[py[v]] |= 1<<px[v]; }
    for(int w=0;w<NWC;w++){ u64 m=cand[w];
        while(m){ int b=__builtin_ctzll(m); m&=m-1; int v=w*64+b;
                  rc[px[v]] |= 1<<py[v]; cc2[py[v]] |= 1<<px[v]; } }
    int br=0; for(int i=0;i<R;i++) br += gcap[rs[i]|rc[i]];
    int bc=0; for(int j=0;j<Cc;j++) bc += gcap[cs[j]|cc2[j]];
    return br<bc?br:bc;
}

static void dfs(int depth, u64 *cand){
    tnodes++;
    if (depth + pc(cand) <= best) return;
    if (capbound(depth,cand) <= best) return;
    if (depth > best){
        #pragma omp critical
        { if(depth>best){ best=depth; bestn=depth; memcpy(bestset,S,depth*sizeof(int));
            printf("BEST %d  t %.2f  SET",best,now());
            for(int i=0;i<depth;i++) printf(" %d,%d",px[bestset[i]],py[bestset[i]]);
            printf("\n"); fflush(stdout); } }
    }
    u64 loc[NWC]; memcpy(loc,cand,sizeof(loc));
    for(;;){
        int v=-1;
        for(int w=0;w<NWC;w++) if(loc[w]){ v=w*64+__builtin_ctzll(loc[w]); break; }
        if(v<0) break;
        loc[v>>6] &= ~(1ULL<<(v&63));
        if (depth+1+pc(loc) <= best) break;
        push(v,depth);
        u64 ch[NWC]; memset(ch,0,sizeof(ch));
        for(int w=0;w<NWC;w++){ u64 m=loc[w];
            while(m){ int b=__builtin_ctzll(m); m&=m-1; int u=w*64+b;
                      if(addable(u,depth+1)) ch[w] |= 1ULL<<b; } }
        dfs(depth+1,ch);
        pop(v,depth);
    }
}

int main(int argc,char**argv){
    R=atoi(argv[1]); Cc=atoi(argv[2]); if(argc>3) best=atoi(argv[3]);
    N=R*Cc;
    if(N>NWC*64){ fprintf(stderr,"N too big\n"); return 1; }
    MAXD=(R-1)*(R-1)+(Cc-1)*(Cc-1);
    if(MAXD>=DW*64){ fprintf(stderr,"MAXD too big\n"); return 1; }
    if(Cc>20||R>20){ fprintf(stderr,"cap table too big\n"); return 1; }
    /* --- relabel cells along anti-diagonals --- */
    { int k=0;
      for(int s=0;s<R+Cc-1;s++) for(int x=0;x<R;x++){ int y=s-x; if(y<0||y>=Cc) continue;
            px[k]=x; py[k]=y; k++; }
      if(k!=N){ fprintf(stderr,"relabel bug\n"); return 1; } }
    DD=malloc((size_t)N*N*sizeof(int));
    for(int a=0;a<N;a++) for(int b=0;b<N;b++){
        int dx=px[a]-px[b], dy=py[a]-py[b]; DD[(size_t)a*N+b]=dx*dx+dy*dy; }
    /* --- gcap: max 3-AP-free subset of a column mask --- */
    int W = (R>Cc?R:Cc);
    gcap=malloc(sizeof(int)<<W);
    for(int m=0;m<(1<<W);m++){
        int free_=1;
        for(int a=0;a<W&&free_;a++) if(m>>a&1)
            for(int c=a+2;c<W;c+=2) if((m>>c&1) && (m>>((a+c)/2)&1)){ free_=0; break; }
        if(free_) gcap[m]=__builtin_popcount(m);
        else { int bst=0; for(int b=0;b<W;b++) if(m>>b&1){ int g=gcap[m^(1<<b)]; if(g>bst) bst=g; }
               gcap[m]=bst; }
    }
    if(best<1){ best=1; bestn=1; bestset[0]=0; }
    double t0=now();
    /* root tasks: first two cells in the relabelled order, no symmetry reduction */
    static int tv0[300000],tv1[300000]; int ntask=0;
    for(int v0=0;v0<N;v0++) for(int v1=v0+1;v1<N;v1++){
        if(2+(N-1-v1)<=best) break;
        tv0[ntask]=v0; tv1[ntask]=v1; ntask++; }
    fprintf(stderr,"tasks %d\n",ntask);
    #pragma omp parallel
    {
      #pragma omp for schedule(dynamic,1)
      for(int t=0;t<ntask;t++){
        int v0=tv0[t],v1=tv1[t];
        if(2+(N-1-v1)<=best) continue;
        push(v0,0); push(v1,1);
        u64 ch[NWC]; memset(ch,0,sizeof(ch));
        for(int u=v1+1;u<N;u++) if(addable(u,2)) bset(ch,u);
        dfs(2,ch);
        pop(v1,1); pop(v0,0);
      }
      #pragma omp atomic
      nodes += tnodes;
    }
    printf("DONE-B grid %dx%d  OPT %d  nodes %lld  time %.2f\n",R,Cc,best,nodes,now()-t0);
    printf("SET"); for(int i=0;i<bestn;i++) printf(" %d,%d",px[bestset[i]],py[bestset[i]]); printf("\n");
    return 0;
}
