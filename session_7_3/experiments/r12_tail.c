/* Round 12 -- is the Delta_2 step-size usage repairable by truncation?
 *
 * At lit/ind.tex line 1172 the step of the supermartingale Z_l^+(v) is
 *     Delta Z_l^+(v) = d_{{v,y_i} up l+1}
 * where y_i is the vertex chosen at step i, drawn UNIFORMLY from V(i).  So the step is
 * not a maximum over pairs; it is the codegree at a random partner.  That is what makes
 * truncation look plausible: cap the step at tau and bound separately the probability
 * that a step ever exceeds tau.
 *
 * Criterion.  P(v sees a big step) ~ i_max * B_v(tau) / N with
 * B_v(tau) = #{ y : codeg(v,y) > tau }.  Summing over the N vertices that must all
 * survive (the stopping time at line 720 halts on the first failure):
 *
 *      sum_v P(v fails)  =  i_max * E_v[ B_v(tau) ]   must be  << 1
 *
 * and for H_n, i_max = zeta N D^{-1/2} (log N)^{1/2} ~ 1.07 zeta n.  So the average
 * number of partners above tau must be much less than 1/n.  Meanwhile tau must stay
 * below D^{1/2 - eps} for the proof to close.  This measures both sides.
 *
 * gcc -O2 -o r12_tail r12_tail.c -lm
 * usage: r12_tail <n> <samples> <seed>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N, RMAX;
static int *vecs, *vstart, *vcnt;

static unsigned long long rs;
static unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

#define PX(i) ((i)%n)
#define PY(i) ((i)/n)

static void build_vecs(void){
    int span=2*n-1;
    vcnt=calloc(RMAX+1,sizeof(int)); vstart=calloc(RMAX+2,sizeof(int));
    for(int dx=-(n-1);dx<=n-1;dx++) for(int dy=-(n-1);dy<=n-1;dy++) vcnt[dx*dx+dy*dy]++;
    int tot=0; for(int r=0;r<=RMAX;r++){ vstart[r]=tot; tot+=vcnt[r]; }
    vstart[RMAX+1]=tot;
    vecs=malloc((size_t)tot*sizeof(int));
    int *fill=malloc((RMAX+1)*sizeof(int));
    memcpy(fill,vstart,(RMAX+1)*sizeof(int));
    for(int dx=-(n-1);dx<=n-1;dx++) for(int dy=-(n-1);dy<=n-1;dy++){
        int r=dx*dx+dy*dy; vecs[fill[r]++]=(dx+n-1)*span+(dy+n-1); }
    free(fill);
}

static int cmp_ll(const void*a,const void*b){
    long long x=*(const long long*)a,y=*(const long long*)b; return (x>y)-(x<y); }

/* deduped list of pairs {u,w} forming an edge of H_n with x */
static long long *buildP(int x,long long *cap,int *out_m){
    int span=2*n-1, xx=PX(x), xy=PY(x);
    static int *bhead=NULL,*bnext=NULL,*cls=NULL;
    if(!bhead){ bhead=malloc((RMAX+1)*sizeof(int)); bnext=malloc(N*sizeof(int)); cls=malloc(N*sizeof(int)); }
    for(int r=0;r<=RMAX;r++) bhead[r]=-1;
    for(int u=0;u<N;u++){ if(u==x) continue;
        int dx=PX(u)-xx,dy=PY(u)-xy,d=dx*dx+dy*dy; bnext[u]=bhead[d]; bhead[d]=u; }
    long long m=0,alloc=*cap; long long *P=malloc((size_t)alloc*sizeof(long long));
    for(int r=0;r<=RMAX;r++){
        if(bhead[r]<0) continue;
        int c=0; for(int u=bhead[r];u>=0;u=bnext[u]) cls[c++]=u;
        if(c<2) continue;
        if(m+(long long)c*(c-1)/2>alloc){ while(m+(long long)c*(c-1)/2>alloc) alloc*=2;
            P=realloc(P,(size_t)alloc*sizeof(long long)); }
        for(int i=0;i<c;i++) for(int j=i+1;j<c;j++){ int a=cls[i],b=cls[j];
            P[m++]=(a<b)?(long long)a*N+b:(long long)b*N+a; }
    }
    for(int a=0;a<N;a++){
        if(a==x) continue;
        int ax=PX(a),ay=PY(a),dx=xx-ax,dy=xy-ay,r=dx*dx+dy*dy;
        for(int t=vstart[r];t<vstart[r+1];t++){
            int p=vecs[t],tx=p/span-(n-1),ty=p%span-(n-1);
            int bx=ax+tx,by=ay+ty;
            if(bx<0||bx>=n||by<0||by>=n) continue;
            int b=by*n+bx; if(b==x||b==a) continue;
            if(m>=alloc){ alloc*=2; P=realloc(P,(size_t)alloc*sizeof(long long)); }
            P[m++]=(a<b)?(long long)a*N+b:(long long)b*N+a;
        }
    }
    qsort(P,(size_t)m,sizeof(long long),cmp_ll);
    long long k=0; for(long long i=0;i<m;i++) if(i==0||P[i]!=P[i-1]) P[k++]=P[i];
    *cap=alloc; *out_m=(int)k; return P;
}

int main(int argc,char**argv){
    n=argc>1?atoi(argv[1]):64;
    int SAMP=argc>2?atoi(argv[2]):40;
    rs=argc>3?(unsigned long long)atoi(argv[3]):777ULL; rs=rs*6364136223846793005ULL+1;
    N=n*n; RMAX=2*(n-1)*(n-1);
    build_vecs();

    long long *codeg=calloc(N,sizeof(long long));
    /* tau ladder, as fractions of n */
    const double frac[]={1.00,0.80,0.65,0.55,0.50,0.40,0.30,0.20};  /* fractions of sqrt(D) */
    const int NF=8;
    double Bsum[8]; for(int f=0;f<NF;f++) Bsum[f]=0;
    double D0=1.75*(double)N*log((double)n);   /* sqrt(D) scale, fixed before the loop */
    long long gmaxcod=0;
    double sumD=0, sumMax=0, sumMean=0, sumKmax=0, sumK90=0;

    for(int s=0;s<SAMP;s++){
        int x=(int)(rnd()%(unsigned long long)N);
        long long cap=1<<20; int m;
        long long *P=buildP(x,&cap,&m);
        memset(codeg,0,(size_t)N*sizeof(long long));
        for(int i=0;i<m;i++){ codeg[P[i]/N]++; codeg[P[i]%N]++; }
        free(P);
        long long mx=0,tot=0;
        for(int y=0;y<N;y++){ if(y==x) continue; tot+=codeg[y]; if(codeg[y]>mx) mx=codeg[y]; }
        for(int f=0;f<NF;f++){
            double tau=frac[f]*sqrt(D0); long long B=0;
            for(int y=0;y<N;y++){ if(y==x) continue; if((double)codeg[y]>tau) B++; }
            Bsum[f]+=(double)B;
        }
        sumD+=(double)m; sumMax+=(double)mx; sumMean+=(double)tot/(N-1);
        if(mx>gmaxcod) gmaxcod=mx;
        /* how big is the cluster at the very top?  (mirror partners) */
        long long kmax=0, k90=0;
        for(int y=0;y<N;y++){ if(y==x) continue;
            if(codeg[y]>=mx) kmax++;
            if((double)codeg[y]>=0.90*(double)mx) k90++; }
        sumKmax+=(double)kmax; sumK90+=(double)k90;
    }
    double D=sumD/SAMP, mxavg=sumMax/SAMP, mnavg=sumMean/SAMP;
    double logN=log((double)N);
    double i_max = (double)N*pow(D,-0.5)*sqrt(logN);      /* zeta = 1 */
    printf("n=%d  N=%d  samples=%d\n",n,N,SAMP);
    printf("  D = %.1f    sqrt(D) = %.1f    D^{1/2} is the target step bound\n",D,sqrt(D));
    printf("  codeg: mean = %.2f   per-vertex max (avg over v) = %.1f   ( = %.3f n )\n",
           mnavg,mxavg,mxavg/(double)n);
    printf("  i_max (zeta=1) = %.1f  = %.3f n\n", i_max, i_max/(double)n);
    printf("  truncation needs  i_max * E_v[B_v(tau)] << 1,  i.e. E_v[B_v] << %.3g\n", 1.0/i_max);
    printf("  tau/n    tau      E_v[B_v(tau)]    i_max*E_v[B_v]   verdict\n");
    for(int f=0;f<NF;f++){
        double E=Bsum[f]/SAMP, crit=i_max*E;
        printf("  %5.2f  %7.1f  %14.4f  %15.4g   %s\n",
               frac[f], frac[f]*sqrt(D0), E, crit, crit<1.0?"ok":"FAILS");
    }
    double kmax=sumKmax/SAMP, k90=sumK90/SAMP;
    printf("  top cluster: partners AT the per-vertex max = %.2f ; within 90%% of it = %.2f\n", kmax, k90);
    printf("  truncate just below the max: i_max * %.2f = %.1f = %.2f n   (needs << 1)\n",
           kmax, i_max*kmax, i_max*kmax/(double)n);
    printf("  Delta_2max/sqrt(D) = %.4f    1/sqrt(log D) = %.4f\n", mxavg/sqrt(D), 1.0/sqrt(log(D)));
    /* Even without truncation: what does Freedman give with C = Delta_2max?
       exponent >= d^2 / (2(v + Cd)) >= d/(2C) in the C-dominated regime, with the best
       case d = D^{1/2}.  A union bound over the N vertices needs exponent >= log N. */
    double expo = sqrt(D)/(2.0*mxavg);
    printf("  Freedman exponent with C = Delta_2max:  d/(2C) = %.3f   needs log N = %.3f\n",
           expo, logN);
    printf("  ==> short by a factor %.2f   (with C = D^{1/2-eps} it would be D^eps, polynomial)\n",
           logN/expo);
    return 0;
}
