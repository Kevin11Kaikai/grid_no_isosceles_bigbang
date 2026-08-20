/* Round 9, probe 9.1 -- does a large Gamma hurt the PROCESS, or only the ANALYSIS?
 *
 * Build 3-uniform ~D-regular hypergraphs on N vertices with Gamma dialled to order:
 *   partition vertices into groups of size k; give each group H "hub pairs" {a,b}
 *   and add edges {v,a,b} for every member v.  Then Gamma(v,v') = H inside a group,
 *   and the fraction of vertex pairs with large Gamma is ~ k/N.
 * Pad with random edges to reach average degree D.
 *
 * BB Thm 1.1 demands Gamma < D^{1-eps}. Run random greedy and compare |I| to the BB
 * conclusion N(ln N/D)^{1/2}. If |I| holds up even when Gamma >> D^{1-eps}, the
 * hypothesis is an artefact of the proof method, not of the truth.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

int main(int argc,char**argv){
    int N=atoi(argv[1]); int D=atoi(argv[2]); int k=atoi(argv[3]); int H=atoi(argv[4]);
    rs=strtoull(argv[5],NULL,10)|1;
    long want=(long)N*D/3;
    long cap=want+ (long)N*H + 16;
    int *E=malloc(cap*3*sizeof(int)); long m=0;
    int *perm=malloc((size_t)N*4);
    for(int i=0;i<N;i++) perm[i]=i;
    for(int i=N-1;i>0;i--){ int j=rnd()%(i+1); int t=perm[i];perm[i]=perm[j];perm[j]=t; }
    if(k>1&&H>0){
        for(int g=0; g+k<=N; g+=k){
            for(int h=0;h<H;h++){
                int a=perm[rnd()%N], b=perm[rnd()%N];
                if(a==b) continue;
                for(int t=0;t<k;t++){
                    int v=perm[g+t]; if(v==a||v==b) continue;
                    if(m>=cap) break;
                    E[3*m]=v; E[3*m+1]=a; E[3*m+2]=b; m++;
                }
            }
        }
    }
    while(m<want){
        int a=rnd()%N,b=rnd()%N,c=rnd()%N;
        if(a==b||b==c||a==c) continue;
        E[3*m]=a;E[3*m+1]=b;E[3*m+2]=c;m++;
    }
    /* incidence lists */
    long *deg=calloc(N,8);
    for(long e=0;e<m;e++){ deg[E[3*e]]++; deg[E[3*e+1]]++; deg[E[3*e+2]]++; }
    long *st=malloc((size_t)(N+1)*8); st[0]=0;
    for(int i=0;i<N;i++) st[i+1]=st[i]+deg[i];
    long tot=st[N];
    int *p1=malloc(tot*sizeof(int)), *p2=malloc(tot*sizeof(int));
    long *fill=malloc((size_t)N*8); memcpy(fill,st,(size_t)N*8);
    for(long e=0;e<m;e++){
        int x=E[3*e],y=E[3*e+1],z=E[3*e+2];
        p1[fill[x]]=y; p2[fill[x]++]=z;
        p1[fill[y]]=x; p2[fill[y]++]=z;
        p1[fill[z]]=x; p2[fill[z]++]=y;
    }
    /* random greedy */
    int *ord=malloc((size_t)N*4); for(int i=0;i<N;i++) ord[i]=i;
    for(int i=N-1;i>0;i--){ int j=rnd()%(i+1); int t=ord[i];ord[i]=ord[j];ord[j]=t; }
    char *sel=calloc(N,1); long I=0;
    for(int t=0;t<N;t++){
        int v=ord[t]; int ok=1;
        for(long e=st[v]; e<st[v+1]; e++){ if(sel[p1[e]]&&sel[p2[e]]){ ok=0; break; } }
        if(ok){ sel[v]=1; I++; }
    }
    double Davg=3.0*m/N;
    double bb=N*sqrt(log((double)N)/Davg);
    printf("N=%d D=%3.0f k=%6d H=%3d | Gamma~%3d  D^0.9=%8.0f  badfrac=%.4f | |I|=%6ld  BB=%7.0f  |I|/BB=%.4f\n",
           N,Davg,k,H,H,pow(Davg,0.9),(k>1&&H>0)?(double)k/N:0.0,I,bb,I/bb);
    return 0;
}
