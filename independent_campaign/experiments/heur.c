/* heur.c -- simulated-annealing / iterated local search for large
 * isosceles-free subsets of a W x H integer grid.
 *
 * State: a k-element multiset-free placement of points.
 * Cost : sum over apexes b in S, over squared distances r, of C(m_{b,r}, 2)
 *        where m_{b,r} = #{a in S\{b} : d2(b,a) = r}.
 *        cost == 0  <=>  S is isosceles-free (exact integer count of
 *        isosceles triples, each counted once at its apex).
 * Move : relocate one point to a free cell.  Delta evaluated in O(k).
 * Schedule: geometric annealing with restarts; outer loop raises k by 1
 *        every time a zero-cost configuration of size k is found.
 *
 * ALL ARITHMETIC IS EXACT INTEGER.
 *
 * USAGE: heur W H [k0] [seconds] [seed] [outfile]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <time.h>
#include <math.h>

static int BW,BH,N,DMAX;
static uint64_t rs;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }
static inline int rndn(int n){ return (int)(rnd()%(uint64_t)n); }

static int K;
static int *pos;          /* pos[i] = cell index of point i */
static int *occ;          /* occ[cell] = point index or -1 */
static int *cnt;          /* cnt[i*(DMAX+1)+r] */
static long long *costi;  /* per-apex cost */
static long long cost;
static int *tmp; static int *tmpstamp; static int stamp=0;

static inline int D2(int p,int q){
    int ax=p%BW, ay=p/BW, bx=q%BW, by=q/BW;
    return (ax-bx)*(ax-bx)+(ay-by)*(ay-by);
}
#define CNT(i,r) cnt[(size_t)(i)*(DMAX+1)+(r)]

static void build(void){
    memset(cnt,0,sizeof(int)*(size_t)K*(DMAX+1));
    cost=0;
    for(int i=0;i<K;i++)
        for(int j=0;j<K;j++) if(j!=i) CNT(i,D2(pos[i],pos[j]))++;
    for(int i=0;i<K;i++){
        long long c=0;
        stamp++;
        for(int j=0;j<K;j++) if(j!=i){
            int r=D2(pos[i],pos[j]);
            if(tmpstamp[r]!=stamp){ tmpstamp[r]=stamp; int m=CNT(i,r); c+=(long long)m*(m-1)/2; }
        }
        costi[i]=c; cost+=c;
    }
}

/* delta of moving point i from pos[i] to cell q (q free) */
static long long delta_move(int i,int q,long long *newci){
    int p=pos[i];
    long long d=0;
    for(int b=0;b<K;b++){
        if(b==i) continue;
        int ro=D2(pos[b],p), rn=D2(pos[b],q);
        if(ro==rn) continue;
        int mo=CNT(b,ro);      /* includes i */
        int mn=CNT(b,rn);
        d += -(long long)(mo-1) + (long long)mn;
    }
    /* new self cost */
    stamp++;
    long long c=0;
    for(int b=0;b<K;b++){ if(b==i) continue; int r=D2(q,pos[b]);
        if(tmpstamp[r]!=stamp){ tmpstamp[r]=stamp; tmp[r]=0; }
        tmp[r]++; }
    stamp++;
    for(int b=0;b<K;b++){ if(b==i) continue; int r=D2(q,pos[b]);
        if(tmpstamp[r]!=stamp){ tmpstamp[r]=stamp; int m=tmp[r]; c+=(long long)m*(m-1)/2; } }
    *newci=c;
    d += c - costi[i];
    return d;
}

static void apply_move(int i,int q,long long newci){
    int p=pos[i];
    for(int b=0;b<K;b++){
        if(b==i) continue;
        int ro=D2(pos[b],p), rn=D2(pos[b],q);
        if(ro==rn) continue;
        int mo=CNT(b,ro), mn=CNT(b,rn);
        costi[b] += -(long long)(mo-1) + (long long)mn;
        CNT(b,ro)=mo-1; CNT(b,rn)=mn+1;
    }
    /* rebuild row i */
    for(int b=0;b<K;b++){ if(b==i) continue; CNT(i,D2(p,pos[b]))--; }
    occ[p]=-1; pos[i]=q; occ[q]=i;
    for(int b=0;b<K;b++){ if(b==i) continue; CNT(i,D2(q,pos[b]))++; }
    costi[i]=newci;
    cost=0; for(int b=0;b<K;b++) cost+=costi[b];
}

static void randinit(void){
    memset(occ,-1,sizeof(int)*N);
    for(int i=0;i<K;i++){ int q; do{q=rndn(N);}while(occ[q]>=0); pos[i]=q; occ[q]=i; }
    build();
}

int main(int argc,char**argv){
    BW=atoi(argv[1]); BH=argc>2?atoi(argv[2]):BW;
    int k0=argc>3?atoi(argv[3]):1;
    double secs=argc>4?atof(argv[4]):10.0;
    rs=argc>5?(uint64_t)atoll(argv[5]):88172645463325252ULL;
    const char*outf=argc>6?argv[6]:NULL;
    if(rs==0) rs=1;
    N=BW*BH; DMAX=(BW-1)*(BW-1)+(BH-1)*(BH-1);
    int KMAX=N<600?N:600;
    pos=malloc(sizeof(int)*KMAX); occ=malloc(sizeof(int)*N);
    cnt=malloc(sizeof(int)*(size_t)KMAX*(DMAX+1));
    costi=malloc(sizeof(long long)*KMAX);
    tmp=malloc(sizeof(int)*(DMAX+2)); tmpstamp=calloc(DMAX+2,sizeof(int));

    int bestk=0; int *bestpos=malloc(sizeof(int)*KMAX);
    clock_t t0=clock();
    K=k0>1?k0:1;
    long long iters=0;
    while((double)(clock()-t0)/CLOCKS_PER_SEC < secs){
        /* one annealing run at current K */
        randinit();
        double T0=2.0, T1=0.02;
        long long steps = 40000LL + 4000LL*K;
        int stall=0;
        for(long long it=0; it<steps && cost>0; it++){
            iters++;
            double T = T0*pow(T1/T0,(double)it/(double)steps);
            /* pick a point, biased to conflicted ones */
            int i;
            if(rnd()&3){
                int tries=0; do{ i=rndn(K); tries++; }while(costi[i]==0 && tries<8);
            } else i=rndn(K);
            int q; do{ q=rndn(N); }while(occ[q]>=0);
            long long nc;
            long long d=delta_move(i,q,&nc);
            if(d<=0 || exp(-(double)d/T) * 4294967296.0 > (double)(rnd()>>32)){
                apply_move(i,q,nc);
            }
            if(cost==0) break;
            (void)stall;
        }
        if(cost==0){
            if(K>bestk){ bestk=K; memcpy(bestpos,pos,sizeof(int)*K);
                fprintf(stderr,"  k=%d found (%.1fs)\n",K,(double)(clock()-t0)/CLOCKS_PER_SEC); }
            K++;
        }
    }
    printf("BOARD %dx%d BEST %d iters %lld\n",BW,BH,bestk,iters);
    if(bestk){
        printf("SET");
        for(int i=0;i<bestk;i++) printf(" %d,%d",bestpos[i]%BW,bestpos[i]/BW);
        printf("\n");
        if(outf){ FILE*f=fopen(outf,"w");
            fprintf(f,"%d %d %d\n",BW,BH,bestk);
            for(int i=0;i<bestk;i++) fprintf(f,"%d %d\n",bestpos[i]%BW,bestpos[i]/BW);
            fclose(f); }
    }
    return 0;
}
