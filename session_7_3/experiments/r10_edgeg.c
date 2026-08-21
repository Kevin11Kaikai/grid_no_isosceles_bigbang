/* Round 10 -- the edge-weighted Gamma distribution.
 *
 * Bennett-Bohman consume Gamma NOT as a max but through the drift of d_l^-(v)
 * (lit/ind.tex line 1017): the error term there is
 *      O( sum_{e in d_l(v)} sum_{{x,x'} subset e minus v} c_{2,2->1}(x,x') )
 * against a main term  ~ d_l(v) * d_2 ~ d_l(v) * D^{1/(r-1)}.
 * For r=3 each edge contributes exactly one pair, so the relevant statistic is
 *      Gamma_edge  :=  sum_{x<y} codeg(x,y) Gamma(x,y) / sum_{x<y} codeg(x,y)
 * i.e. Gamma averaged over pairs WEIGHTED BY HOW MANY EDGES CONTAIN THE PAIR.
 *
 * Bad pairs are mirror pairs, which have long perpendicular bisectors, hence
 * LARGE codegree.  So the edge measure may be biased TOWARD the bad pairs.
 * This program measures whether it is.
 *
 * For a sampled vertex x one pass yields Gamma(x,y) and codeg(x,y) for every y.
 *   P(x) = { {u,w} : {x,u,w} in H_n }        (built exactly, deduped)
 *   Gamma(x,y) = |P(x) cap P(y)| = #{ {u,w} in P(x) : {y,u,w} in H_n }
 * so we enumerate P(x) and, for each pair, every y completing it to an edge.
 *
 * gcc -O2 -o r10_edgeg r10_edgeg.c -lm
 * usage: r10_edgeg <n> <samples> <seed>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N, RMAX;
static int *vecs;                   /* packed (dx+n-1)*(2n-1)+(dy+n-1) */
static int *vstart, *vcnt;

static unsigned long long rs;
static unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

#define PX(i) ((i)%n)
#define PY(i) ((i)/n)

static void build_vecs(void){
    int span = 2*n-1;
    vcnt   = calloc(RMAX+1, sizeof(int));
    vstart = calloc(RMAX+2, sizeof(int));
    for(int dx=-(n-1); dx<=n-1; dx++)
        for(int dy=-(n-1); dy<=n-1; dy++)
            vcnt[dx*dx+dy*dy]++;
    int tot=0;
    for(int r=0;r<=RMAX;r++){ vstart[r]=tot; tot+=vcnt[r]; }
    vstart[RMAX+1]=tot;
    vecs = malloc((size_t)tot*sizeof(int));
    int *fill = malloc((RMAX+1)*sizeof(int));
    memcpy(fill, vstart, (RMAX+1)*sizeof(int));
    for(int dx=-(n-1); dx<=n-1; dx++)
        for(int dy=-(n-1); dy<=n-1; dy++){
            int r=dx*dx+dy*dy;
            vecs[fill[r]++] = (dx+n-1)*span + (dy+n-1);
        }
    free(fill);
}

static int cmp_ll(const void *a, const void *b){
    long long x=*(const long long*)a, y=*(const long long*)b;
    return (x>y)-(x<y);
}

/* P(x): sorted, deduped list of pairs {u,w} (key = min*N+max) forming an edge with x */
static long long *buildP(int x, long long *cap, int *out_m){
    int span=2*n-1;
    int xx=PX(x), xy=PY(x);
    static int *bhead=NULL, *bnext=NULL, *cls=NULL;
    if(!bhead){ bhead=malloc((RMAX+1)*sizeof(int)); bnext=malloc(N*sizeof(int)); cls=malloc(N*sizeof(int)); }
    for(int r=0;r<=RMAX;r++) bhead[r]=-1;
    for(int u=0;u<N;u++){
        if(u==x) continue;
        int dx=PX(u)-xx, dy=PY(u)-xy, d=dx*dx+dy*dy;
        bnext[u]=bhead[d]; bhead[d]=u;
    }
    long long m=0, alloc=*cap;
    long long *P = malloc((size_t)alloc*sizeof(long long));
    /* case A: x is the apex -- all pairs at equal distance from x */
    for(int r=0;r<=RMAX;r++){
        if(bhead[r]<0) continue;
        int c=0;
        for(int u=bhead[r]; u>=0; u=bnext[u]) cls[c++]=u;
        if(c<2) continue;
        if(m + (long long)c*(c-1)/2 > alloc){
            while(m + (long long)c*(c-1)/2 > alloc) alloc*=2;
            P=realloc(P,(size_t)alloc*sizeof(long long));
        }
        for(int i=0;i<c;i++) for(int j=i+1;j<c;j++){
            int a=cls[i], b=cls[j];
            P[m++] = (a<b) ? (long long)a*N+b : (long long)b*N+a;
        }
    }
    /* case B: some a != x is the apex, with |a-x| = |a-b| */
    for(int a=0;a<N;a++){
        if(a==x) continue;
        int ax=PX(a), ay=PY(a);
        int dx=xx-ax, dy=xy-ay, r=dx*dx+dy*dy;
        for(int t=vstart[r]; t<vstart[r+1]; t++){
            int p=vecs[t], tx=p/span-(n-1), ty=p%span-(n-1);
            int bx=ax+tx, by=ay+ty;
            if(bx<0||bx>=n||by<0||by>=n) continue;
            int b=by*n+bx;
            if(b==x||b==a) continue;
            if(m>=alloc){ alloc*=2; P=realloc(P,(size_t)alloc*sizeof(long long)); }
            P[m++] = (a<b) ? (long long)a*N+b : (long long)b*N+a;
        }
    }
    qsort(P, (size_t)m, sizeof(long long), cmp_ll);
    long long k=0;
    for(long long i=0;i<m;i++) if(i==0||P[i]!=P[i-1]) P[k++]=P[i];
    *cap = alloc; *out_m = (int)k;
    return P;
}

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):48;
    int SAMP = argc>2?atoi(argv[2]):100;
    rs = argc>3?(unsigned long long)atoi(argv[3]):12345ULL; rs=rs*6364136223846793005ULL+1;
    N=n*n; RMAX=2*(n-1)*(n-1);
    build_vecs();

    int span=2*n-1;
    long long *cnt   = calloc(N,sizeof(long long));
    long long *codeg = calloc(N,sizeof(long long));
    int *seen = calloc(N,sizeof(int));
    int stamp=0;

    double sum_unif=0, sum_edge=0, sum_max=0, sum_maxE=0, sum_D=0;
    double sum_d2u=0, sum_d2e=0, sum_d2m=0;
    for(int s=0;s<SAMP;s++){
        int x = (int)(rnd()%(unsigned long long)N);
        long long cap=1<<20; int m;
        long long *P = buildP(x,&cap,&m);
        memset(cnt,0,(size_t)N*sizeof(long long));
        memset(codeg,0,(size_t)N*sizeof(long long));
        for(int i=0;i<m;i++){
            int u=(int)(P[i]/N), w=(int)(P[i]%N);
            codeg[u]++; codeg[w]++;
            int ux=PX(u),uy=PY(u),wx=PX(w),wy=PY(w);
            int dx=wx-ux, dy=wy-uy, r=dx*dx+dy*dy;
            stamp++;
            /* (i) y on the perpendicular bisector of u,w */
            long long K = (long long)wx*wx+(long long)wy*wy-(long long)ux*ux-(long long)uy*uy;
            if(dx!=0){
                for(int yy=0;yy<n;yy++){
                    long long num = K - 2LL*yy*dy;
                    long long den = 2LL*dx;
                    if(num%den) continue;
                    long long yx = num/den;
                    if(yx<0||yx>=n) continue;
                    int y=(int)(yy*n+yx);
                    if(y==u||y==w||y==x) continue;
                    if(seen[y]==stamp) continue; seen[y]=stamp; cnt[y]++;
                }
            } else {
                for(int yx=0;yx<n;yx++){
                    long long num = K, den = 2LL*dy;
                    if(num%den) continue;
                    long long yy=num/den;
                    if(yy<0||yy>=n) continue;
                    int y=(int)(yy*n+yx);
                    if(y==u||y==w||y==x) continue;
                    if(seen[y]==stamp) continue; seen[y]=stamp; cnt[y]++;
                }
            }
            /* (ii) u apex: |u-y| = |u-w| ; (iii) w apex: |w-y| = |w-u| */
            for(int pass=0;pass<2;pass++){
                int ax = pass? wx:ux, ay = pass? wy:uy;
                int other = pass? u:w;
                for(int t=vstart[r]; t<vstart[r+1]; t++){
                    int p=vecs[t], tx=p/span-(n-1), ty=p%span-(n-1);
                    int yx=ax+tx, yy=ay+ty;
                    if(yx<0||yx>=n||yy<0||yy>=n) continue;
                    int y=yy*n+yx;
                    if(y==u||y==w||y==x||y==other) continue;
                    if(seen[y]==stamp) continue; seen[y]=stamp; cnt[y]++;
                }
            }
        }
        free(P);
        long long tot=0, totE=0, mx=0, mxE=0, wsum=0, csq=0, cmx=0;
        for(int y=0;y<N;y++){
            if(y==x) continue;
            tot += cnt[y];
            if(cnt[y]>mx) mx=cnt[y];
            if(codeg[y]>cmx) cmx=codeg[y];
            if(codeg[y]>0){
                totE += codeg[y]*cnt[y]; wsum += codeg[y];
                csq  += codeg[y]*codeg[y];
                if(cnt[y]>mxE) mxE=cnt[y];
            }
        }
        sum_d2u += (double)wsum/(N-1);
        sum_d2e += wsum? (double)csq/(double)wsum : 0;
        sum_d2m += (double)cmx;
        sum_unif += (double)tot/(N-1);
        sum_edge += wsum? (double)totE/(double)wsum : 0;
        sum_max  += (double)mx;
        sum_maxE += (double)mxE;
        sum_D    += (double)m;
    }
    double D = sum_D/SAMP;
    double gu = sum_unif/SAMP, ge = sum_edge/SAMP;
    double gm = sum_max/SAMP, gme = sum_maxE/SAMP;
    double logN = log((double)N);
    printf("n=%d  N=%d  samples=%d\n", n,N,SAMP);
    printf("  D (mean vertex degree)      = %.1f   = %.3f n^2 ln n\n", D, D/((double)N*log((double)n)));
    printf("  sqrt(D)                     = %.1f\n", sqrt(D));
    printf("  Gamma  uniform-pair  mean   = %.2f      /D = %.5f\n", gu, gu/D);
    printf("  Gamma  EDGE-weighted mean   = %.2f      /D = %.5f\n", ge, ge/D);
    printf("  Gamma  max over all pairs   = %.1f      /D = %.5f\n", gm, gm/D);
    printf("  Gamma  max over co-edge prs = %.1f      /D = %.5f\n", gme, gme/D);
    printf("  bias  edge/uniform          = %.3f\n", ge/gu);
    printf("  criterion  1/sqrt(log N)    = %.5f     1/log D = %.5f\n",
           1.0/sqrt(logN), 1.0/log(D));
    printf("  VERDICT edge-mean vs 1/sqrt(log N): %s\n",
           (ge/D < 1.0/sqrt(logN)) ? "PASS (drift error lower order)" : "FAIL");
    double d2u=sum_d2u/SAMP, d2e=sum_d2e/SAMP, d2m=sum_d2m/SAMP, sD=sqrt(D);
    printf("  --- Delta_2 = codegree of a pair; BB needs < D^(1/2-eps), sqrt(D)=%.1f\n", sD);
    printf("  Delta_2 uniform-pair  mean  = %.2f      /sqrt(D) = %.5f\n", d2u, d2u/sD);
    printf("  Delta_2 EDGE-weighted mean  = %.2f      /sqrt(D) = %.5f\n", d2e, d2e/sD);
    printf("  Delta_2 max                 = %.1f      /sqrt(D) = %.5f\n", d2m, d2m/sD);
    return 0;
}
