/* Round 11 -- can H_n be regularised without breaking the other hypotheses?
 *
 * H_n is not D-regular (Dmax/Davg = 1.470, Dmax/Dmin = 2.26..2.64).  BB Thm 1.1 needs
 * D-regular.  The standard repair is to ADD edges until every vertex has degree Dmax:
 * an independent set in H_n u R is independent in H_n, so any lower bound survives, and
 * the conclusion Omega(N (log N / D)^{1/2}) only pays sqrt(Dmax/Davg) = 1.21.
 *
 * The repair is only legitimate if R does not itself violate the Delta_2 and Gamma
 * conditions.  R is built by the configuration model on the deficiency degrees
 * r(v) = Dmax - deg_{H_n}(v), independently of H_n, so heuristically
 *
 *     Delta_2(R) ~ 3|R| / C(N,2)      ~  2 Dmax / N        =  O(log n)
 *     Gamma_R(v,v') ~ |P_R(v)| |P_R(v')| / (N^2/2) ~ 2 Dmax^2/N^2 = O(log^2 n)
 *
 * against Delta_2(H_n) ~ n and Gamma(H_n) ~ 0.5 n^2.  This measures both directly.
 *
 * gcc -O2 -o r11_dummy r11_dummy.c -lm
 * usage: r11_dummy <n> <pair-samples> <seed>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static unsigned long long rs;
static unsigned long long rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

static int cmp_ll(const void *a, const void *b){
    long long x=*(const long long*)a, y=*(const long long*)b;
    return (x>y)-(x<y);
}

int main(int argc,char**argv){
    int n = argc>1?atoi(argv[1]):32;
    int SAMP = argc>2?atoi(argv[2]):200;
    rs = argc>3?(unsigned long long)atoi(argv[3]):4242ULL; rs=rs*6364136223846793005ULL+1;
    long N=(long)n*n;
    int RMAX=2*(n-1)*(n-1);

    /* ---- exact degrees of H_n (same computation as r11_reg.c) ---- */
    int *cnt=malloc((size_t)(RMAX+1)*sizeof(int));
    long long *deg=calloc((size_t)N,sizeof(long long));
    int *px=malloc((size_t)N*sizeof(int)), *py=malloc((size_t)N*sizeof(int));
    for(long i=0;i<N;i++){ px[i]=(int)(i%n); py[i]=(int)(i/n); }
    for(long x=0;x<N;x++){
        memset(cnt,0,(size_t)(RMAX+1)*sizeof(int));
        int xx=px[x],xy=py[x];
        for(long a=0;a<N;a++){ if(a==x) continue; int dx=px[a]-xx,dy=py[a]-xy; cnt[dx*dx+dy*dy]++; }
        long long apex=0;
        for(long a=0;a<N;a++){ if(a==x) continue; int dx=px[a]-xx,dy=py[a]-xy;
            int c=cnt[dx*dx+dy*dy]-1; apex+=c; deg[a]+=c; }
        deg[x]+=apex/2;
    }
    long long Dmax=0, tot=0;
    for(long a=0;a<N;a++){ tot+=deg[a]; if(deg[a]>Dmax) Dmax=deg[a]; }
    double Davg=(double)tot/(double)N;

    /* ---- deficiency stubs, configuration model ---- */
    long long stubs=0;
    for(long a=0;a<N;a++) stubs += Dmax-deg[a];
    while(stubs%3) { Dmax++; stubs=0; for(long a=0;a<N;a++) stubs += Dmax-deg[a]; }
    printf("n=%d  N=%ld  Davg=%.1f  Dmax=%lld  Dmax/Davg=%.4f\n",n,N,Davg,Dmax,Dmax/Davg);
    printf("  deficiency stubs = %lld  -> |R| ~ %lld edges (%.4f of |E(H_n)|)\n",
           stubs, stubs/3, (double)(stubs/3)/(double)(tot/3));

    int *stub=malloc((size_t)stubs*sizeof(int));
    long long k=0;
    for(long a=0;a<N;a++) for(long long j=0;j<Dmax-deg[a];j++) stub[k++]=(int)a;
    for(long long i=stubs-1;i>0;i--){ long long j=(long long)(rnd()%(unsigned long long)(i+1));
        int t=stub[i]; stub[i]=stub[j]; stub[j]=t; }

    long long nE=stubs/3, kept=0, rejected=0;
    int *E=malloc((size_t)nE*3*sizeof(int));
    for(long long i=0;i+2<stubs;i+=3){
        int a=stub[i],b=stub[i+1],c=stub[i+2];
        if(a==b||b==c||a==c){ rejected++; continue; }
        E[3*kept]=a; E[3*kept+1]=b; E[3*kept+2]=c; kept++;
    }
    printf("  configuration model: %lld edges kept, %lld rejected (repeated vertex)\n",kept,rejected);

    /* ---- Delta_2(R) = max codegree of a pair in R ---- */
    unsigned int *cod=calloc((size_t)N*(size_t)N,sizeof(unsigned int));
    if(!cod){ printf("  (codegree table too large, skipping Delta_2)\n"); return 1; }
    for(long long i=0;i<kept;i++){
        int a=E[3*i],b=E[3*i+1],c=E[3*i+2];
        cod[(size_t)a*N+b]++; cod[(size_t)b*N+a]++;
        cod[(size_t)a*N+c]++; cod[(size_t)c*N+a]++;
        cod[(size_t)b*N+c]++; cod[(size_t)c*N+b]++;
    }
    unsigned int d2max=0; double d2sum=0;
    for(size_t i=0;i<(size_t)N*(size_t)N;i++){ if(cod[i]>d2max) d2max=cod[i]; d2sum+=cod[i]; }
    printf("  Delta_2(R): max = %u   mean = %.3f   (predicted 6|R|/N(N-1) = %.3f)\n",
           d2max, d2sum/((double)N*(double)(N-1)),
           6.0*(double)kept/((double)N*(double)(N-1)));
    free(cod);

    /* ---- Gamma_R(v,v') = |P_R(v) cap P_R(v')| over sampled pairs ---- */
    long long *Pv=malloc((size_t)(Dmax+8)*sizeof(long long));
    long long *Pw=malloc((size_t)(Dmax+8)*sizeof(long long));
    double gsum=0; long long gmax=0;
    for(int s=0;s<SAMP;s++){
        int v=(int)(rnd()%(unsigned long long)N), w=(int)(rnd()%(unsigned long long)N);
        if(v==w) { s--; continue; }
        long long mv=0,mw=0;
        for(long long i=0;i<kept;i++){
            int a=E[3*i],b=E[3*i+1],c=E[3*i+2];
            int o1=-1,o2=-1;
            if(a==v){o1=b;o2=c;} else if(b==v){o1=a;o2=c;} else if(c==v){o1=a;o2=b;}
            if(o1>=0) Pv[mv++] = (o1<o2)?(long long)o1*N+o2:(long long)o2*N+o1;
            o1=-1;
            if(a==w){o1=b;o2=c;} else if(b==w){o1=a;o2=c;} else if(c==w){o1=a;o2=b;}
            if(o1>=0) Pw[mw++] = (o1<o2)?(long long)o1*N+o2:(long long)o2*N+o1;
        }
        qsort(Pv,(size_t)mv,sizeof(long long),cmp_ll);
        qsort(Pw,(size_t)mw,sizeof(long long),cmp_ll);
        long long i=0,j=0,g=0;
        while(i<mv&&j<mw){ if(Pv[i]<Pw[j]) i++; else if(Pv[i]>Pw[j]) j++; else {g++;i++;j++;} }
        gsum+=(double)g; if(g>gmax) gmax=g;
    }
    double lg=log((double)n);
    printf("  Gamma_R over %d random pairs: mean = %.3f  max = %lld   (predicted 2(Dmax-Davg)^2/N^2 = %.2f)\n",
           SAMP, gsum/SAMP, gmax, 2.0*((double)Dmax-Davg)*((double)Dmax-Davg)/((double)N*(double)N));
    printf("  compare H_n:  Delta_2 ~ %d (= n)    Gamma ~ %.0f (= 0.5 n^2)    ln^2 n = %.2f\n",
           n, 0.5*(double)n*(double)n, lg*lg);
    return 0;
}
