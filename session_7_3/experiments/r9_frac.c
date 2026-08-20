/* Round 9, probe 9.2 -- Gamma ISOLATED, via a matched control.
 *
 * TREATMENT: pair the vertices by a random perfect matching. For each matched pair
 *   (v,v') and each of H hub pairs {a,b}, add BOTH {v,a,b} and {v',a,b}.
 *   => Gamma(v,v') = H, concentrated on a perfect matching of pairs.
 * CONTROL:   identical in every other respect -- same edge count, same codegree 2 on
 *   every hub pair, same mean degree -- except the two edges of each hub pair go to
 *   two INDEPENDENT random vertices.  => Gamma stays ~O(1), spread out.
 *
 * Same D, same Delta_2, same edge multiset structure. ONLY Gamma differs.
 * If |I| agrees, Gamma does not affect the process, only the proof.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <math.h>
static uint64_t rs;
static inline uint64_t rnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

static long greedy(int N,long m,int *E){
    long *deg=calloc(N,8);
    for(long e=0;e<m;e++){ deg[E[3*e]]++; deg[E[3*e+1]]++; deg[E[3*e+2]]++; }
    long *st=malloc((size_t)(N+1)*8); st[0]=0;
    for(int i=0;i<N;i++) st[i+1]=st[i]+deg[i];
    int *p1=malloc(st[N]*sizeof(int)), *p2=malloc(st[N]*sizeof(int));
    long *fill=malloc((size_t)N*8); memcpy(fill,st,(size_t)N*8);
    for(long e=0;e<m;e++){
        int x=E[3*e],y=E[3*e+1],z=E[3*e+2];
        p1[fill[x]]=y; p2[fill[x]++]=z;
        p1[fill[y]]=x; p2[fill[y]++]=z;
        p1[fill[z]]=x; p2[fill[z]++]=y;
    }
    int *ord=malloc((size_t)N*4); for(int i=0;i<N;i++) ord[i]=i;
    for(int i=N-1;i>0;i--){ int j=rnd()%(i+1); int t=ord[i];ord[i]=ord[j];ord[j]=t; }
    char *sel=calloc(N,1); long I=0;
    for(int t=0;t<N;t++){
        int v=ord[t]; int ok=1;
        for(long e=st[v];e<st[v+1];e++) if(sel[p1[e]]&&sel[p2[e]]){ ok=0; break; }
        if(ok){ sel[v]=1; I++; }
    }
    free(deg);free(st);free(p1);free(p2);free(fill);free(ord);free(sel);
    return I;
}
int main(int argc,char**argv){
    int N=atoi(argv[1]); int D=atoi(argv[2]); int H=atoi(argv[3]); int P=atoi(argv[5]);
    unsigned long long seed=strtoull(argv[4],NULL,10)|1;
    long want=(long)N*D/3;
    long cap=want+(long)N*H*P+64;
    int *E=malloc(cap*3*sizeof(int));
    int *perm=malloc((size_t)N*4);
    long res[2];
    for(int mode=0;mode<2;mode++){          /* 0 = treatment, 1 = control */
        rs=seed; long m=0;
        for(int i=0;i<N;i++) perm[i]=i;
        for(int i=N-1;i>0;i--){ int j=rnd()%(i+1); int t=perm[i];perm[i]=perm[j];perm[j]=t; }
        if(H>0) for(int rep=0; rep<P; rep++){
            for(int i=N-1;i>0;i--){ int j=rnd()%(i+1); int t=perm[i];perm[i]=perm[j];perm[j]=t; }
            for(int g=0; g+1<N; g+=2){
                for(int h=0;h<H;h++){
                    int a=rnd()%N, b=rnd()%N; if(a==b) continue;
                    int v1,v2;
                    if(mode==0){ v1=perm[g]; v2=perm[g+1]; }
                    else       { v1=rnd()%N; v2=rnd()%N; }
                    if(v1==a||v1==b||v2==a||v2==b||v1==v2) continue;
                    if(m+2>cap) break;
                    E[3*m]=v1;E[3*m+1]=a;E[3*m+2]=b;m++;
                    E[3*m]=v2;E[3*m+1]=a;E[3*m+2]=b;m++;
                }
            }
        }
        while(m<want){
            int a=rnd()%N,b=rnd()%N,c=rnd()%N;
            if(a==b||b==c||a==c) continue;
            E[3*m]=a;E[3*m+1]=b;E[3*m+2]=c;m++;
        }
        res[mode]=greedy(N,m,E);
    }
    double Davg=(double)D;
    double bb=N*sqrt(log((double)N)/Davg);
    printf("N=%d D=%d H=%3d (Gamma/D=%.2f) | treat |I|=%6ld  control |I|=%6ld  ratio=%.4f | BB=%7.0f\n",
           N,D,H,(double)H/D,res[0],res[1],(double)res[0]/res[1],bb);
    return 0;
}
