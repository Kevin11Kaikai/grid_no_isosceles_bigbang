/* s8_line.c -- counterexample search against Lemma E (line-restricted codegree sum).
 *
 * Lemma E claims, for L a line of the plane and z in [n]^2:
 *     z not in L :   sum_{u in L cap [n]^2} codeg(u,z)  =  O(n^{3/2})
 *     z in L     :   sum_{u in L cap [n]^2} codeg(u,z)  =  O(n^2 / s_L^2)
 * where s_L is the sup-norm of L's primitive direction.
 *
 * This program computes the exact sums for every line of primitive direction of sup-norm
 * <= SMAX (which is where the sums are largest, since such lines carry the most points)
 * and reports max / n^{3/2} over lines missing z, and max * s_L^2 / n^2 over lines through z.
 * A growing ratio in the first column would refute Lemma E.
 *
 * Computation is used here ONLY to look for a counterexample; the lemma is proved in
 * THEOREM_AND_PROOF.md Part VI.
 *
 * build: gcc -O2 -o s8_line s8_line.c -lm
 * run:   ./s8_line <n>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

#define SMAX 6

static int n, N, RMAX;
static int *vhead, *vnext, *vxa, *vxb, *cntz;

static int igcd(int a,int b){ if(a<0)a=-a; if(b<0)b=-b; while(b){int t=a%b;a=b;b=t;} return a; }
static long long egcd(long long a,long long b,long long*x,long long*y){
    if(b==0){*x=1;*y=0;return a;} long long x1,y1,g=egcd(b,a%b,&x1,&y1);
    *x=y1;*y=x1-(a/b)*y1; return g; }
static int inside(int a,int b){ return a>=0&&a<n&&b>=0&&b<n; }

static long bisector_count(int p,int q,int u,int w){
    long long dx=u-p, dy=w-q;
    long long K=(long long)u*u+(long long)w*w-(long long)p*p-(long long)q*q;
    long long A=2*dx,B=2*dy;
    long long g=igcd((int)(A<0?-A:A),(int)(B<0?-B:B));
    if(g==0) return 0; if(K%g) return 0;
    long long a=A/g,b=B/g,c=K/g,s,t; egcd(a,b,&s,&t);
    long long x0=s*c,y0=t*c;
    double lo=-1e18,hi=1e18;
    if(b>0){double l=(double)(x0-(n-1))/b,h=(double)x0/b; if(l>lo)lo=l; if(h<hi)hi=h;}
    else if(b<0){double l=(double)x0/b,h=(double)(x0-(n-1))/b; if(l>lo)lo=l; if(h<hi)hi=h;}
    else if(x0<0||x0>n-1) return 0;
    if(a>0){double l=(double)(-y0)/a,h=(double)((n-1)-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h;}
    else if(a<0){double l=(double)((n-1)-y0)/a,h=(double)(-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h;}
    else if(y0<0||y0>n-1) return 0;
    long long klo=(long long)ceil(lo-1e-9), khi=(long long)floor(hi+1e-9);
    long cnt=0;
    for(long long k=klo;k<=khi;k++){ long long X=x0-b*k,Y=y0+a*k;
        if(X>=0&&X<n&&Y>=0&&Y<n) cnt++; }
    return cnt;
}

/* codeg(u=(uu,uw), z=(zp,zq)); cntz is the distance histogram centred at z */
static int codeg_uz(int uu,int uw,int zp,int zq){
    if(uu==zp&&uw==zq) return 0;
    int dx=uu-zp,dy=uw-zq,d=dx*dx+dy*dy;
    long c = cntz[d]-1;                                  /* apex z */
    if(inside(2*zp-uu,2*zq-uw)) c-=1;
    long cu=0;                                           /* apex u */
    for(int e=vhead[d]; e!=-1; e=vnext[e]){
        int X=uu+vxa[e],Y=uw+vxb[e]; if(inside(X,Y)) cu++;
    }
    cu-=1; if(inside(2*uu-zp,2*uw-zq)) cu-=1;
    c+=cu;
    long cb=bisector_count(zp,zq,uu,uw);                 /* apex on bisector */
    if(((uu+zp)%2==0)&&((uw+zq)%2==0)&&inside((uu+zp)/2,(uw+zq)/2)) cb-=1;
    c+=cb;
    return c<0?0:(int)c;
}

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):128;
    N=n*n; RMAX=2*(n-1)*(n-1);
    vhead=malloc(sizeof(int)*(RMAX+1));
    for(int i=0;i<=RMAX;i++) vhead[i]=-1;
    int cap=(2*n-1)*(2*n-1);
    vnext=malloc(sizeof(int)*cap); vxa=malloc(sizeof(int)*cap); vxb=malloc(sizeof(int)*cap);
    int nv=0;
    for(int a=-(n-1);a<=n-1;a++)for(int b=-(n-1);b<=n-1;b++){
        if(!a&&!b) continue; int d=a*a+b*b; if(d>RMAX) continue;
        vxa[nv]=a;vxb[nv]=b;vnext[nv]=vhead[d];vhead[d]=nv;nv++;
    }
    cntz=malloc(sizeof(int)*(RMAX+1));

    int zp=n/2, zq=n/3;                 /* generic z, not on the grid diagonal */
    memset(cntz,0,sizeof(int)*(RMAX+1));
    for(int x=0;x<n;x++)for(int y=0;y<n;y++){
        int dx=x-zp,dy=y-zq; if(!dx&&!dy) continue; cntz[dx*dx+dy*dy]++;
    }
    /* codeg(.,z) for the whole grid */
    int *cg=malloc(sizeof(int)*N);
    for(int x=0;x<n;x++)for(int y=0;y<n;y++) cg[x*n+y]=codeg_uz(x,y,zp,zq);

    double n15=pow((double)n,1.5), n2=(double)n*n;
    double bestOff=0, bestOn=0; int boa=0,bob=0; long bestOffPts=0;
    printf("n=%d  z=(%d,%d)   [Lemma E: off-line sum = O(n^{3/2}), on-line = O(n^2/s_L^2)]\n",
           n,zp,zq);
    for(int a=-SMAX;a<=SMAX;a++)for(int b=0;b<=SMAX;b++){
        if(a==0&&b==0) continue;
        if(b==0&&a<0) continue;
        if(igcd(a,b)!=1) continue;
        int sL = (abs(a)>b?abs(a):b);
        /* lines with direction (a,b): u0 + k(a,b). Sweep all start points on the boundary. */
        for(int sx=0;sx<n;sx++)for(int sy=0;sy<n;sy++){
            /* canonical: only start if (sx,sy)-(a,b) is outside the grid */
            if(inside(sx-a,sy-b)) continue;
            long long sum=0; long pts=0; int through=0;
            for(int k=0;;k++){
                int X=sx+k*a, Y=sy+k*b;
                if(!inside(X,Y)) break;
                sum += cg[X*n+Y]; pts++;
                if(X==zp&&Y==zq) through=1;
            }
            if(pts<2) continue;
            if(through){
                double val=(double)sum*sL*sL/n2;
                if(val>bestOn) bestOn=val;
            } else {
                double val=(double)sum/n15;
                if(val>bestOff){ bestOff=val; boa=a; bob=b; bestOffPts=pts; }
            }
        }
    }
    printf("  max over lines MISSING z  (dir sup-norm <= %d):  sum/n^{3/2} = %.4f   (dir=(%d,%d), %ld pts)\n",
           SMAX, bestOff, boa, bob, bestOffPts);
    printf("  max over lines THROUGH  z  (dir sup-norm <= %d):  sum*s_L^2/n^2 = %.4f\n",
           SMAX, bestOn);
    return 0;
}
