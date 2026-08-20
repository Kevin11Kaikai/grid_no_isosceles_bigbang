/* Round 8, probe 8.1 -- DISTRIBUTION of Gamma(v,v') over vertex pairs of H_n.
 * Gamma(v,v') = |P(v) n P(v')|, P(v) = { {a,b} : {v,a,b} isosceles }.
 * BB's hypothesis is on the MAXIMUM. Question: how rare are the bad pairs, and
 * what is the typical value?  P(v) built in O(n^2 log n) via lattice-vectors-by-norm.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static int n; static long N;
static int *vx,*vy; static long *vstart;
static uint64_t *tab, TCAP, TMASK; static uint32_t *tstamp, tcur;
static int *cls,*key; static long *bucket; static long maxk;

static inline void tclear(void){ tcur++; if(tcur==0){ memset(tstamp,0,TCAP*4); tcur=1; } }
static inline int tadd(uint64_t k){
    uint64_t h=(k*1146111111111111ULL)&TMASK;
    while(tstamp[h]==tcur){ if(tab[h]==k) return 1; h=(h+1)&TMASK; }
    tstamp[h]=tcur; tab[h]=k; return 0;
}
static inline int thas(uint64_t k){
    uint64_t h=(k*1146111111111111ULL)&TMASK;
    while(tstamp[h]==tcur){ if(tab[h]==k) return 1; h=(h+1)&TMASK; }
    return 0;
}
static long doP(int vX,int vY,int collect,long *cnt){
    long hits=0;
    for(long i=0;i<N;i++){ int ax=i%n, ay=i/n; key[i]=(ax-vX)*(ax-vX)+(ay-vY)*(ay-vY); }
    memset(bucket,0,(maxk+2)*8);
    for(long i=0;i<N;i++) bucket[key[i]+1]++;
    for(long r=0;r<maxk+1;r++) bucket[r+1]+=bucket[r];
    for(long i=0;i<N;i++) cls[bucket[key[i]]++]=i;
    long i=0;
    while(i<N){
        long j=i; int k0=key[cls[i]];
        while(j<N && key[cls[j]]==k0) j++;
        if(k0!=0){
            for(long p=i;p<j;p++) for(long q=p+1;q<j;q++){
                long a=cls[p], b=cls[q];
                uint64_t k=(a<b)?((uint64_t)a*N+b):((uint64_t)b*N+a);
                if(collect){ if(!tadd(k)) (*cnt)++; } else if(thas(k)) hits++;
            }
        }
        i=j;
    }
    for(long t2=0;t2<N;t2++){
        int ax=t2%n, ay=t2/n; if(ax==vX&&ay==vY) continue;
        long r=(long)(ax-vX)*(ax-vX)+(long)(ay-vY)*(ay-vY);
        for(long t=vstart[r]; t<vstart[r+1]; t++){
            int bx=ax+vx[t], by=ay+vy[t];
            if(bx<0||bx>=n||by<0||by>=n) continue;
            if(bx==vX&&by==vY) continue;
            long b=(long)by*n+bx; if(b==t2) continue;
            uint64_t k=(t2<b)?((uint64_t)t2*N+b):((uint64_t)b*N+t2);
            if(collect){ if(!tadd(k)) (*cnt)++; } else if(thas(k)) hits++;
        }
    }
    return hits;
}
static int cmpl(const void*a,const void*b){ long long x=*(const long long*)a,y=*(const long long*)b; return (x>y)-(x<y); }
static uint64_t rs=88172645463325252ULL;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc,char**argv){
    n=atoi(argv[1]); int samples=atoi(argv[2]); N=(long)n*n;
    maxk=2L*(n-1)*(n-1);
    long *cntr=calloc(maxk+2,8);
    for(int dx=-(n-1);dx<=n-1;dx++)for(int dy=-(n-1);dy<=n-1;dy++){
        long r=(long)dx*dx+(long)dy*dy; if(r<=maxk) cntr[r+1]++; }
    vstart=malloc((maxk+2)*8); vstart[0]=0;
    for(long r=0;r<=maxk;r++) vstart[r+1]=vstart[r]+cntr[r+1];
    long tot=vstart[maxk+1]; vx=malloc(tot*4); vy=malloc(tot*4);
    long *fill=malloc((maxk+2)*8); memcpy(fill,vstart,(maxk+2)*8);
    for(int dx=-(n-1);dx<=n-1;dx++)for(int dy=-(n-1);dy<=n-1;dy++){
        long r=(long)dx*dx+(long)dy*dy; if(r<=maxk){ vx[fill[r]]=dx; vy[fill[r]]=dy; fill[r]++; } }
    cls=malloc(N*4); key=malloc(N*4); bucket=malloc((maxk+2)*8);
    TCAP=1; while(TCAP < (uint64_t)(16.0*N*log((double)n))) TCAP<<=1;
    TMASK=TCAP-1; tab=malloc(TCAP*8); tstamp=calloc(TCAP,4); tcur=0;

    long long *vals=malloc((size_t)samples*sizeof(long long)), *gvals=malloc((size_t)samples*sizeof(long long));
    long mx=0, nstruct=0, ngen=0; double sum=0, sumgen=0;
    for(int s=0;s<samples;s++){
        long i=rnd()%N, j=rnd()%N; while(j==i) j=rnd()%N;
        int ax=i%n, ay=i/n, bx=j%n, by=j/n;
        int st=(ax==bx)||(ay==by)||(ax-bx==ay-by)||(ax-bx==by-ay);
        long c=0; tclear(); doP(ax,ay,1,&c);
        long h=doP(bx,by,0,&c);
        vals[s]=h; sum+=h; if(h>mx) mx=h;
        if(st) nstruct++; else { gvals[ngen++]=h; sumgen+=h; }
    }
    qsort(vals,samples,sizeof(long long),cmpl); qsort(gvals,ngen,sizeof(long long),cmpl);
    printf("n=%4d  ALL(%d): mean=%8.1f med=%6lld p90=%6lld p99=%7lld max=%7ld\n",
           n,samples,sum/samples,vals[samples/2],vals[(long)(samples*0.90)],
           vals[(long)(samples*0.99)],mx);
    printf("        structured sampled %ld/%d = %.4f  (predicted 4/n = %.4f)\n",
           nstruct,samples,(double)nstruct/samples,4.0/n);
    printf("        GENERIC(%ld): mean=%7.1f med=%6lld p99=%7lld max=%7lld | mean/n=%.3f med/n=%.3f\n",
           ngen,sumgen/ngen,gvals[ngen/2],gvals[(long)(ngen*0.99)],gvals[ngen-1],
           (sumgen/ngen)/n,(double)gvals[ngen/2]/n);
    return 0;
}
