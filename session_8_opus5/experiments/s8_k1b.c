/* s8_k1b.c -- counterexample search against obligation K1b.
 *
 * K1b (HANDOFF):  sum_{u in L} c_{2,2->1}(u, y, i)  =  O(n^{3/2})
 *   for every line L, every y in V(i), every i <= T.
 *
 * Exact combinatorial description used (proved in THEOREM_AND_PROOF Part VIII):
 *   for u,w in V(i),   {u,w} is a size-2 edge of H(i)  <=>  exists z in I(i) with
 *   {u,w,z} a nondegenerate isosceles triple of H_n.  Hence
 *       c_{2,2->1}(u,y,i) = #{ w in V(i) : {u,w} and {y,w} both size-2 edges }
 *                         = |N(u,i) cap N(y,i)| ,
 *       S_L(y,i)          = e_{G(i)}( L cap V(i), N(y,i) ).
 *
 * This program takes an EXPLICIT independent set I (not a simulation of the process),
 * computes V(i) = {v : no z,z' in I with {v,z,z'} isosceles} exactly, then computes
 * S_L(y,i) exactly for L = the bottom row and y = (0,2).
 *
 * The configuration tested is  I_k = {(0,0)} union {(a,2) : a in A},  A a set of odd
 * integers >= 3 with pairwise gaps >= 6 and Sidon (no a+a' = a''+a''' nontrivially).
 * Claim under test:  S_L(y,i) = Theta(k n), so k = Theta(sqrt n) attains Theta(n^{3/2}).
 *
 * Computation is used here only as a counterexample search against a precisely stated
 * bound; nothing asymptotic is inferred from it.
 *
 * build: gcc -O2 -o s8_k1b s8_k1b.c -lm
 * run:   ./s8_k1b <n> <k>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N;

static int inside(int a,int b){ return a>=0&&a<n&&b>=0&&b<n; }

/* is {p,q,r} a NONDEGENERATE isosceles triple? (squared distances) */
static int iso(int px,int py,int qx,int qy,int rx,int ry){
    long long d1=(long long)(px-qx)*(px-qx)+(long long)(py-qy)*(py-qy);
    long long d2=(long long)(px-rx)*(px-rx)+(long long)(py-ry)*(py-ry);
    long long d3=(long long)(qx-rx)*(qx-rx)+(long long)(qy-ry)*(qy-ry);
    if(d1==0||d2==0||d3==0) return 0;
    /* collinear? cross product */
    long long cr=(long long)(qx-px)*(ry-py)-(long long)(qy-py)*(rx-px);
    if(cr==0) return 0;
    return (d1==d2)||(d1==d3)||(d2==d3);
}

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):128;
    int k = argc>2?atoi(argv[2]):11;
    N=n*n;

    /* build A: odd, >=3, 3-AP-free (greedy).  3-AP-freeness is what keeps the
       vertices u=(a,0) unblocked; it is the only constraint imposed here, so k can
       run well past sqrt(n) and the program reports what actually survives. */
    int *A=malloc(sizeof(int)*(k+2)); int na=0;
    char *sums=calloc(4*n+8,1);
    for(int a=3; a<n && na<k; a+=2){
        int ok=1;
        for(int j=0;j<na && ok;j++) if(sums[a+A[j]]) ok=0;
        if(sums[2*a]) ok=0;
        if(!ok) continue;
        for(int j=0;j<na;j++) sums[a+A[j]]=1;
        sums[2*a]=1;
        A[na++]=a;
    }
    if(na<k){ printf("n=%d: only found k=%d (asked %d)\n", n, na, k); }
    k=na;

    /* I = {(0,0)} union {(a,2): a in A} */
    int ni=k+1;
    int *ix=malloc(sizeof(int)*ni), *iy=malloc(sizeof(int)*ni);
    ix[0]=0; iy[0]=0;
    for(int j=0;j<k;j++){ ix[j+1]=A[j]; iy[j+1]=2; }

    /* verify I is independent */
    int bad=0;
    for(int a=0;a<ni;a++)for(int b=a+1;b<ni;b++)for(int c=b+1;c<ni;c++)
        if(iso(ix[a],iy[a],ix[b],iy[b],ix[c],iy[c])) bad++;
    printf("n=%d  k=%d  |I|=%d   independent: %s (%d violating triples)\n",
           n,k,ni, bad?"NO":"YES", bad);
    if(bad){ return 1; }

    /* V = unblocked vertices */
    char *alive=malloc(N); memset(alive,1,N);
    for(int a=0;a<ni;a++)for(int b=a+1;b<ni;b++)
        for(int vx=0;vx<n;vx++)for(int vy=0;vy<n;vy++){
            if(!alive[vx*n+vy]) continue;
            if((vx==ix[a]&&vy==iy[a])||(vx==ix[b]&&vy==iy[b])) continue;
            if(iso(vx,vy,ix[a],iy[a],ix[b],iy[b])) alive[vx*n+vy]=0;
        }
    for(int a=0;a<ni;a++) alive[ix[a]*n+iy[a]]=0;   /* chosen vertices leave V */
    long nv=0; for(int i=0;i<N;i++) nv+=alive[i];

    /* N(v,i) = { w in V : exists z in I with {v,w,z} isosceles } */
    char *Ny=calloc(N,1);
    int yx=0, yy=2;
    if(!alive[yx*n+yy]){ printf("  y=(0,2) is NOT in V -- configuration invalid\n"); return 1; }
    for(int wx=0;wx<n;wx++)for(int wy=0;wy<n;wy++){
        if(!alive[wx*n+wy]) continue;
        if(wx==yx&&wy==yy) continue;
        for(int a=0;a<ni;a++) if(iso(yx,yy,wx,wy,ix[a],iy[a])){ Ny[wx*n+wy]=1; break; }
    }
    long dy=0; for(int i=0;i<N;i++) dy+=Ny[i];

    /* S_L = sum_{u in L cap V} |N(u) cap N(y)| ,  L = bottom row */
    long long S=0; long uAlive=0; long long mx=0;
    for(int ux=0;ux<n;ux++){
        int uy=0;
        if(!alive[ux*n+uy]) continue;
        uAlive++;
        long long c=0;
        for(int wx=0;wx<n;wx++)for(int wy=0;wy<n;wy++){
            if(!Ny[wx*n+wy]) continue;
            if(wx==ux&&wy==uy) continue;
            for(int a=0;a<ni;a++) if(iso(ux,uy,wx,wy,ix[a],iy[a])){ c++; break; }
        }
        S+=c; if(c>mx) mx=c;
    }
    double n15=pow((double)n,1.5);
    printf("  |V|=%ld  d_2(y)=%ld  |L cap V|=%ld\n", nv, dy, uAlive);
    printf("  S_L(y) = %lld    S_L/n^{3/2} = %.4f    S_L/(k n) = %.4f    max_u c = %lld\n",
           S, S/n15, (double)S/((double)k*n), mx);
    return 0;
}
