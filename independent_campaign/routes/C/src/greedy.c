/* Route C -- randomised greedy + ruin-and-recreate LOWER-BOUND search.
 * Produces "best found" values only (never an exhaustive claim).
 * usage: greedy R C seconds [seed]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <omp.h>

#ifndef NWC
#define NWC 20            /* up to 1280 cells -> 32x32 and beyond */
#endif
typedef uint64_t u64;
static int R,Cc,N,MAXD;
static u64 *circ, *bis; static int *dst;
static volatile int best=0; static int bestset[2000], bestn=0;

static inline void bset(u64*a,int i){a[i>>6]|=1ULL<<(i&63);}
static inline int pcn(const u64*a){int s=0;for(int i=0;i<NWC;i++)s+=__builtin_popcountll(a[i]);return s;}

static inline uint64_t xr(uint64_t *s){ uint64_t x=*s; x^=x<<13; x^=x>>7; x^=x<<17; return *s=x; }

int main(int argc,char**argv){
    R=atoi(argv[1]); Cc=atoi(argv[2]); double secs=atof(argv[3]);
    uint64_t seed0 = (argc>4)? (uint64_t)atoll(argv[4]) : 12345;
    N=R*Cc; if(N>NWC*64){fprintf(stderr,"too big\n");return 1;}
    MAXD=(R-1)*(R-1)+(Cc-1)*(Cc-1);
    dst=malloc((size_t)N*N*sizeof(int));
    circ=calloc((size_t)N*(MAXD+1)*NWC,sizeof(u64));
    bis=calloc((size_t)N*N*NWC,sizeof(u64));
    for(int a=0;a<N;a++)for(int b=0;b<N;b++){
        int dx=a/Cc-b/Cc, dy=a%Cc-b%Cc; int d=dx*dx+dy*dy;
        dst[(size_t)a*N+b]=d; if(a!=b) bset(circ+((size_t)a*(MAXD+1)+d)*NWC,b); }
    for(int a=0;a<N;a++)for(int b=0;b<N;b++){ u64*m=bis+((size_t)a*N+b)*NWC;
        for(int u=0;u<N;u++) if(dst[(size_t)u*N+a]==dst[(size_t)u*N+b]) bset(m,u); }
    double t0=omp_get_wtime();
    #pragma omp parallel
    {
      uint64_t s = seed0 + 0x9E3779B97F4A7C15ULL*(omp_get_thread_num()+1);
      int S[2000], ns;
      int keep[2000];
      u64 cand[NWC];
      int nk=0;
      while(omp_get_wtime()-t0 < secs){
        /* ruin: keep a random sub-multiset of the incumbent */
        ns=0;
        if(nk>0){ for(int i=0;i<nk;i++) if((xr(&s)&15)>3) S[ns++]=keep[i]; }
        /* rebuild candidate set consistent with S */
        for(int w=0;w<NWC;w++) cand[w]=0;
        for(int u=0;u<N;u++) bset(cand,u);
        int ok=1;
        for(int i=0;i<ns && ok;i++){
            int v=S[i];
            if(!((cand[v>>6]>>(v&63))&1ULL)){ ok=0; break; }
            cand[v>>6] &= ~(1ULL<<(v&63));
            for(int j=0;j<i;j++){ int b=S[j]; int d=dst[(size_t)v*N+b];
                const u64*m1=circ+((size_t)b*(MAXD+1)+d)*NWC;
                const u64*m2=circ+((size_t)v*(MAXD+1)+d)*NWC;
                const u64*m3=bis+((size_t)v*N+b)*NWC;
                for(int w=0;w<NWC;w++) cand[w]&=~(m1[w]|m2[w]|m3[w]); }
        }
        if(!ok){ nk=0; continue; }
        /* recreate: random greedy */
        for(;;){
            int c=pcn(cand); if(c==0) break;
            int pick=(int)(xr(&s)%(uint64_t)c);
            int v=-1;
            for(int w=0;w<NWC && v<0;w++){ u64 m=cand[w];
                while(m){ int b=__builtin_ctzll(m); m&=m-1; if(pick--==0){ v=w*64+b; break; } } }
            cand[v>>6]&=~(1ULL<<(v&63));
            for(int j=0;j<ns;j++){ int b=S[j]; int d=dst[(size_t)v*N+b];
                const u64*m1=circ+((size_t)b*(MAXD+1)+d)*NWC;
                const u64*m2=circ+((size_t)v*(MAXD+1)+d)*NWC;
                const u64*m3=bis+((size_t)v*N+b)*NWC;
                for(int w=0;w<NWC;w++) cand[w]&=~(m1[w]|m2[w]|m3[w]); }
            S[ns++]=v;
        }
        if(ns>=nk){ nk=ns; memcpy(keep,S,ns*sizeof(int)); }
        if(ns>best){
            #pragma omp critical
            { if(ns>best){ best=ns; bestn=ns; memcpy(bestset,S,ns*sizeof(int));
                printf("FOUND %d  t %.1f  SET",ns,omp_get_wtime()-t0);
                for(int i=0;i<ns;i++) printf(" %d,%d",bestset[i]/Cc,bestset[i]%Cc);
                printf("\n"); fflush(stdout); } }
        }
      }
    }
    printf("GREEDY %dx%d bestfound %d\n",R,Cc,best);
    return 0;
}
