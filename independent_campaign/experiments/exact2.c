/* exact2.c -- exhaustive maximum isosceles-free subset of a W x H integer grid.
 *
 * See exact.c for the basic idea.  exact2 adds:
 *   (a) Tomita/MCS-style COLOUR-ORDERED pruning.  At every node we pick an
 *       apex s in S and partition the candidate set P into "shells"
 *       {q in P : d2(s,q) = r}.  Because s is IN S, any isosceles-free
 *       extension contains at most ONE point of each shell, i.e. the shells
 *       are cliques of the induced conflict graph.  Sorting shells by size
 *       (largest = colour 1) and numbering vertices by their shell's colour,
 *       we walk the candidates in DECREASING colour and stop the whole loop
 *       as soon as depth + colour(v) <= incumbent: every vertex still left
 *       has colour <= colour(v) and colours are cliques, so at most
 *       colour(v) more points can ever be added.  Sound and much sharper
 *       than a single scalar bound.
 *   (b) task-parallel root decomposition at a chosen depth.
 *   (c) enumeration mode: list all isosceles-free sets of a given size
 *       (up to the symmetry restriction on the minimum-index point).
 *
 * USAGE: exact2 W H [lb] [threads] [taskdepth] [enumsize] [outfile]
 *   lb        : only look for sets strictly larger than lb (0 = full search)
 *   enumsize  : if >0, enumerate every set of exactly this size instead
 * ALL ARITHMETIC IS EXACT INTEGER.
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

static int BW, BH, N, NW;
static u64 *bad;
static int *dx2;
static int DMAX;
static int gbest;
static int gbestset[1024];
static int ENUM = 0;             /* enumeration target size, 0 = optimise */
static FILE *efp = NULL;
static long long ecount = 0;

#define BADP(p,s) (bad + ((size_t)(p)*N + (s))*NW)
static inline int px(int i){ return i % BW; }
static inline int py(int i){ return i / BW; }

static inline int popcnt_arr(const u64 *a){
    int c=0; for(int i=0;i<NW;i++) c += __builtin_popcountll(a[i]); return c;
}

static void precompute(void){
    dx2 = malloc(sizeof(int)*(size_t)N*N);
    for(int p=0;p<N;p++) for(int q=0;q<N;q++){
        int ax=px(p),ay=py(p),bx=px(q),by=py(q);
        dx2[(size_t)p*N+q]=(ax-bx)*(ax-bx)+(ay-by)*(ay-by);
    }
    DMAX = (BW-1)*(BW-1)+(BH-1)*(BH-1);
    size_t sz=(size_t)N*N*NW;
    bad = calloc(sz,sizeof(u64));
    if(!bad){fprintf(stderr,"OOM\n");exit(1);}
    for(int p=0;p<N;p++) for(int s=p+1;s<N;s++){
        int dps=dx2[(size_t)p*N+s];
        u64 *bp=BADP(p,s);
        const int *dp=dx2+(size_t)p*N, *ds=dx2+(size_t)s*N;
        for(int q=0;q<N;q++){
            if(q==p||q==s) continue;
            if(dp[q]==dps||ds[q]==dps||dp[q]==ds[q]) bp[q>>6]|=1ULL<<(q&63);
        }
        memcpy(BADP(s,p),bp,sizeof(u64)*NW);
    }
}

typedef struct {
    int S[256];
    int lbest, lsetn;
    int lset[1024];
    long long nodes;
    /* scratch, per depth */
    u64 *stack;          /* NW*(N+2) */
    int *ordbuf;         /* N*(N+2) */
    int *colbuf;         /* N*(N+2) */
    int *shellhead;      /* DMAX+1 */
    int *shellnext;      /* N */
    int *shellsz;
    int *dlist;
    long long ecnt;
    FILE *out;
} Ctx;

/* Partition P by squared distance from apex s; fill order/colour arrays.
 * Returns the number of colour classes (= a valid upper bound on how many
 * points of P a valid extension may contain).  Vertices are written into
 * ord[] grouped by class with classes sorted by DECREASING size, and
 * col[i] = 1-based class index of ord[i]. */
static int colour_order(Ctx *c,int s,const u64 *P,int *ord,int *col)
{
    int nd=0;
    const int *drow = dx2 + (size_t)s*N;
    for(int w=0;w<NW;w++){
        u64 x=P[w];
        while(x){
            int q=w*64+__builtin_ctzll(x); x&=x-1;
            int r=drow[q];
            if(c->shellhead[r]==-1){ c->dlist[nd++]=r; c->shellsz[r]=0; }
            c->shellnext[q]=c->shellhead[r];
            c->shellhead[r]=q;
            c->shellsz[r]++;
        }
    }
    /* classes sorted by DECREASING size: largest class gets colour 1 */
    int maxs=0; for(int i=0;i<nd;i++) if(c->shellsz[c->dlist[i]]>maxs) maxs=c->shellsz[c->dlist[i]];
    int wpos=0, colour=0;
    for(int sz=maxs; sz>=1; sz--){
        for(int i=0;i<nd;i++){
            int r=c->dlist[i];
            if(c->shellsz[r]!=sz) continue;
            colour++;
            for(int q=c->shellhead[r]; q!=-1; q=c->shellnext[q]){
                ord[wpos]=q; col[wpos]=colour; wpos++;
            }
        }
    }
    for(int i=0;i<nd;i++) c->shellhead[c->dlist[i]]=-1;
    return colour;
}

static void expand(Ctx *c,int depth,u64 *P)
{
    c->nodes++;
    int cnt=popcnt_arr(P);
    if(cnt==0) return;
    if(!ENUM && depth+cnt<=c->lbest) return;
    if(ENUM && depth+cnt<ENUM) return;

    /* choose the apex giving the fewest colour classes (try a few) */
    int *ord = c->ordbuf + (size_t)depth*N;
    int *col = c->colbuf + (size_t)depth*N;
    int lim = depth<4?depth:4;
    int bestk=cnt+1, bestapex=c->S[depth-1];
    for(int t=0;t<lim;t++){
        int s=c->S[depth-1-t];
        int nd=0;
        const int *drow=dx2+(size_t)s*N;
        for(int w=0;w<NW;w++){ u64 x=P[w]; while(x){int q=w*64+__builtin_ctzll(x);x&=x-1;
            int r=drow[q]; if(c->shellhead[r]==-1){c->shellhead[r]=-2;c->dlist[nd++]=r;} } }
        for(int i=0;i<nd;i++) c->shellhead[c->dlist[i]]=-1;
        if(nd<bestk){bestk=nd;bestapex=s;}
    }
    if(!ENUM && depth+bestk<=c->lbest) return;
    if(ENUM && depth+bestk<ENUM) return;

    int k = colour_order(c,bestapex,P,ord,col);
    (void)k;
    u64 *nextP = c->stack + (size_t)depth*NW;

    for(int i=cnt-1;i>=0;i--){
        int v=ord[i];
        if(!ENUM){ if(depth+col[i]<=c->lbest) return; }
        else      { if(depth+col[i]<ENUM) return; }
        P[v>>6] &= ~(1ULL<<(v&63));
        c->S[depth]=v;
        if(ENUM){
            if(depth+1==ENUM){
                c->ecnt++;
                if(c->out){
                    fprintf(c->out,"%d",ENUM);
                    for(int j=0;j<ENUM;j++) fprintf(c->out," %d %d",px(c->S[j]),py(c->S[j]));
                    fputc('\n',c->out);
                }
                continue;
            }
        } else if(depth+1>c->lbest){
            c->lbest=depth+1; c->lsetn=depth+1;
            memcpy(c->lset,c->S,sizeof(int)*(depth+1));
        }
        memcpy(nextP,P,sizeof(u64)*NW);
        for(int t=0;t<depth;t++){
            const u64 *b=BADP(v,c->S[t]);
            for(int w=0;w<NW;w++) nextP[w]&=~b[w];
        }
        expand(c,depth+1,nextP);
    }
}

static int in_fund(int p){
    int x=px(p),y=py(p),bi=y*BW+x;
    int xs[8],ys[8],k=0;
    xs[k]=x;ys[k]=y;k++;  xs[k]=BW-1-x;ys[k]=y;k++;
    xs[k]=x;ys[k]=BH-1-y;k++; xs[k]=BW-1-x;ys[k]=BH-1-y;k++;
    if(BW==BH){ xs[k]=y;ys[k]=x;k++; xs[k]=BH-1-y;ys[k]=x;k++;
                xs[k]=y;ys[k]=BW-1-x;k++; xs[k]=BH-1-y;ys[k]=BW-1-x;k++; }
    for(int i=0;i<k;i++) if(ys[i]*BW+xs[i] < bi) return 0;
    return 1;
}

/* ---- task generation: enumerate all search nodes at depth TD ---- */
typedef struct { int S[8]; u64 *P; } Task;
static Task *tasks; static long ntask=0, captask=0;

static void gen(Ctx *c,int depth,u64 *P,int TD){
    if(depth==TD){
        if(ntask==captask){ captask=captask?captask*2:1024;
            tasks=realloc(tasks,sizeof(Task)*captask); }
        tasks[ntask].P = malloc(sizeof(u64)*NW);
        memcpy(tasks[ntask].P,P,sizeof(u64)*NW);
        for(int i=0;i<TD;i++) tasks[ntask].S[i]=c->S[i];
        ntask++;
        return;
    }
    int cnt=popcnt_arr(P);
    if(cnt==0) return;
    int *ord=c->ordbuf+(size_t)depth*N, *col=c->colbuf+(size_t)depth*N;
    int k=colour_order(c,c->S[depth-1],P,ord,col); (void)k;
    u64 *nextP=c->stack+(size_t)depth*NW;
    for(int i=cnt-1;i>=0;i--){
        int v=ord[i];
        P[v>>6]&=~(1ULL<<(v&63));
        c->S[depth]=v;
        memcpy(nextP,P,sizeof(u64)*NW);
        for(int t=0;t<depth;t++){
            const u64 *b=BADP(v,c->S[t]);
            for(int w=0;w<NW;w++) nextP[w]&=~b[w];
        }
        gen(c,depth+1,nextP,TD);
    }
}

static Ctx *newctx(int lb){
    Ctx *c=calloc(1,sizeof(Ctx));
    c->stack=malloc(sizeof(u64)*(size_t)NW*(N+2));
    c->ordbuf=malloc(sizeof(int)*(size_t)N*(N+2));
    c->colbuf=malloc(sizeof(int)*(size_t)N*(N+2));
    c->shellhead=malloc(sizeof(int)*(DMAX+2));
    c->shellsz=malloc(sizeof(int)*(DMAX+2));
    c->shellnext=malloc(sizeof(int)*N);
    c->dlist=malloc(sizeof(int)*(DMAX+2));
    for(int i=0;i<=DMAX+1;i++) c->shellhead[i]=-1;
    c->lbest=lb; c->lsetn=0; c->nodes=0; c->ecnt=0; c->out=NULL;
    return c;
}

int main(int argc,char**argv){
    BW=atoi(argv[1]); BH=argc>2?atoi(argv[2]):BW;
    int lb=argc>3?atoi(argv[3]):0;
    int nthreads=argc>4?atoi(argv[4]):1;
    int TD=argc>5?atoi(argv[5]):2;
    ENUM=argc>6?atoi(argv[6]):0;
    const char*outf=argc>7?argv[7]:NULL;
    N=BW*BH; NW=(N+63)/64;
    precompute();
    gbest=lb;
    clock_t t0=clock();

    Ctx *g=newctx(lb);
    u64 *P0=malloc(sizeof(u64)*NW);
    for(int v0=0;v0<N;v0++){
        if(!in_fund(v0)) continue;
        memset(P0,0,sizeof(u64)*NW);
        for(int q=v0+1;q<N;q++) P0[q>>6]|=1ULL<<(q&63);
        g->S[0]=v0;
        if(TD<=1){
            if(ntask==captask){captask=captask?captask*2:1024;tasks=realloc(tasks,sizeof(Task)*captask);}
            tasks[ntask].P=malloc(sizeof(u64)*NW);
            memcpy(tasks[ntask].P,P0,sizeof(u64)*NW);
            tasks[ntask].S[0]=v0; ntask++;
        } else gen(g,1,P0,TD);
    }
    fprintf(stderr,"tasks: %ld\n",ntask);

    long long tot=0; long long tote=0;
#ifdef _OPENMP
    omp_set_num_threads(nthreads);
#endif
#pragma omp parallel
    {
        Ctx *c=newctx(lb);
        if(ENUM&&outf){
            char nm[512];
#ifdef _OPENMP
            snprintf(nm,sizeof nm,"%s.%d",outf,omp_get_thread_num());
#else
            snprintf(nm,sizeof nm,"%s.0",outf);
#endif
            c->out=fopen(nm,"w");
        }
        u64 *Pw=malloc(sizeof(u64)*NW);
#pragma omp for schedule(dynamic,1)
        for(long t=0;t<ntask;t++){
            if(!ENUM){
#pragma omp critical
                { if(gbest>c->lbest) c->lbest=gbest; }
            }
            memcpy(Pw,tasks[t].P,sizeof(u64)*NW);
            for(int i=0;i<(TD<1?1:TD);i++) c->S[i]=tasks[t].S[i];
            int d=(TD<1?1:TD);
            if(!ENUM && d>c->lbest){ c->lbest=d; c->lsetn=d; memcpy(c->lset,c->S,sizeof(int)*d); }
            if(ENUM && d==ENUM){ c->ecnt++; }
            else expand(c,d,Pw);
#pragma omp critical
            {
                if(!ENUM && c->lbest>gbest && c->lsetn==c->lbest){
                    gbest=c->lbest; memcpy(gbestset,c->lset,sizeof(int)*gbest);
                }
            }
        }
#pragma omp critical
        { tot+=c->nodes; tote+=c->ecnt; if(c->out) fclose(c->out); }
    }
    double el=(double)(clock()-t0)/CLOCKS_PER_SEC;
    if(ENUM) printf("BOARD %dx%d  ENUM size %d  count %lld  nodes %lld  time %.2fs\n",
                    BW,BH,ENUM,tote,tot,el);
    else {
        printf("BOARD %dx%d  OPT %d  nodes %lld  time %.2fs\n",BW,BH,gbest,tot,el);
        if(gbest>lb||lb==0){
            printf("SET");
            for(int i=0;i<gbest;i++) printf(" %d,%d",px(gbestset[i]),py(gbestset[i]));
            printf("\n");
        } else printf("NOSET (no set larger than lb=%d exists; upper bound %d CERTIFIED)\n",lb,lb);
    }
    return 0;
}
