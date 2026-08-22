/* s8_tail.c -- exact one-step increment law for d_2(v) in the isosceles hypergraph H_n.
 *
 * For a fixed vertex v of the n x n grid, computes codeg(v,y) for every y != v, where
 *   codeg(v,y) = # { x : {v,y,x} is a NONDEGENERATE isosceles triple }.
 * This is exactly the one-step increment of d_2^+(v) at step 0 of the random greedy
 * process when the algorithm selects y, so the empirical law over y is the law of the
 * increment (up to the monotone shrinking of H(i)).
 *
 * Purpose: check the analytic claims
 *   (T1)  B_v(tau) := #{y : codeg(v,y) > tau}  <=  32 n^2 / tau      [Pareto(1) tail]
 *   (T2)  Delta_2  := max_y codeg(v,y)         =   Theta(n)
 *   (T3)  E_y[codeg(v,y)] = 2D/N               =   Theta(log n)
 * The proofs are in THEOREM_AND_PROOF.md; this is a sanity check, not evidence.
 *
 * build:  gcc -O2 -o s8_tail s8_tail.c -lm
 * run:    ./s8_tail <n> [num_v]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N;
static int *cntv;        /* cntv[d] = #{z in grid : |vz|^2 = d} */
static int RMAX;
/* lattice vectors grouped by squared norm, CSR */
static int *vhead, *vnext, *vx, *vy_, nvec;

static int igcd(int a, int b){ if(a<0)a=-a; if(b<0)b=-b; while(b){int t=a%b;a=b;b=t;} return a; }

/* extended gcd: returns g, sets x,y with a*x+b*y=g */
static long long egcd(long long a, long long b, long long *x, long long *y){
    if(b==0){ *x=1; *y=0; return a; }
    long long x1,y1; long long g=egcd(b,a%b,&x1,&y1);
    *x=y1; *y=x1-(a/b)*y1; return g;
}

static int inside(int a,int b){ return a>=0 && a<n && b>=0 && b<n; }

/* number of lattice points of [0,n)^2 on the perpendicular bisector of v=(p,q), y=(u,w) */
static long bisector_count(int p,int q,int u,int w){
    long long dx = u-p, dy = w-q;
    long long K = (long long)u*u + (long long)w*w - (long long)p*p - (long long)q*q; /* 2<x,d> = K */
    /* line: 2*dx*x + 2*dy*y = K */
    long long A = 2*dx, B = 2*dy;
    long long g = igcd((int)(A<0?-A:A),(int)(B<0?-B:B));
    if(g==0) return 0;
    if(K % g) return 0;                 /* no lattice points at all */
    long long a=A/g, b=B/g, c=K/g;      /* a*x + b*y = c, gcd(a,b)=1 */
    long long s,t; egcd(a,b,&s,&t);     /* a*s + b*t = 1 */
    long long x0 = s*c, y0 = t*c;       /* particular solution */
    /* general: (x0 - b*k, y0 + a*k) */
    /* need 0 <= x0 - b*k <= n-1 and 0 <= y0 + a*k <= n-1 */
    double lo = -1e18, hi = 1e18;
    if(b > 0){ double l = (double)(x0-(n-1))/b, h = (double)x0/b; if(l>lo)lo=l; if(h<hi)hi=h; }
    else if(b < 0){ double l = (double)x0/b, h = (double)(x0-(n-1))/b; if(l>lo)lo=l; if(h<hi)hi=h; }
    else { if(x0<0 || x0>n-1) return 0; }
    if(a > 0){ double l = (double)(-y0)/a, h = (double)((n-1)-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h; }
    else if(a < 0){ double l = (double)((n-1)-y0)/a, h = (double)(-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h; }
    else { if(y0<0 || y0>n-1) return 0; }
    long long klo = (long long)ceil(lo - 1e-9), khi = (long long)floor(hi + 1e-9);
    /* verify endpoints defensively */
    while(klo<=khi){ long long X=x0-b*klo, Y=y0+a*klo; if(X>=0&&X<n&&Y>=0&&Y<n) break; klo++; }
    while(khi>=klo){ long long X=x0-b*khi, Y=y0+a*khi; if(X>=0&&X<n&&Y>=0&&Y<n) break; khi--; }
    if(khi<klo) return 0;
    return (long)(khi-klo+1);
}

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):64;
    int numv = argc>2?atoi(argv[2]):5;
    N = n*n; RMAX = 2*(n-1)*(n-1);

    /* lattice vectors by squared norm */
    vhead = malloc(sizeof(int)*(RMAX+1));
    for(int i=0;i<=RMAX;i++) vhead[i]=-1;
    int cap = (2*n-1)*(2*n-1);
    vnext = malloc(sizeof(int)*cap); vx = malloc(sizeof(int)*cap); vy_ = malloc(sizeof(int)*cap);
    nvec=0;
    for(int a=-(n-1);a<=n-1;a++) for(int b=-(n-1);b<=n-1;b++){
        if(a==0&&b==0) continue;
        int d=a*a+b*b; if(d>RMAX) continue;
        vx[nvec]=a; vy_[nvec]=b; vnext[nvec]=vhead[d]; vhead[d]=nvec; nvec++;
    }
    cntv = malloc(sizeof(int)*(RMAX+1));

    /* choose v's: centre, quarter, corner, and two generic */
    int vs[16][2]; int nv=0;
    vs[nv][0]=n/2;   vs[nv][1]=n/2;   nv++;
    vs[nv][0]=n/4;   vs[nv][1]=n/3;   nv++;
    vs[nv][0]=0;     vs[nv][1]=0;     nv++;
    vs[nv][0]=n/2+1; vs[nv][1]=n/3+2; nv++;
    vs[nv][0]=n-1;   vs[nv][1]=n/2;   nv++;
    if(numv<nv) nv=numv;

    printf("n=%d  N=%d\n", n, N);
    printf("%-12s %10s %10s %10s %12s %10s\n",
           "v","deg_pairs","mean","max=D2","max/n","B(n/8)");
    double logn = log((double)n);

    int *codeg = malloc(sizeof(int)*N);
    for(int vi=0; vi<nv; vi++){
        int p=vs[vi][0], q=vs[vi][1];
        memset(cntv,0,sizeof(int)*(RMAX+1));
        for(int a=0;a<n;a++)for(int b=0;b<n;b++){
            int dx=a-p, dy=b-q; if(!dx&&!dy) continue; cntv[dx*dx+dy*dy]++;
        }
        long long total=0; int mx=0;
        for(int u=0;u<n;u++)for(int w=0;w<n;w++){
            int idx=u*n+w;
            if(u==p&&w==q){ codeg[idx]=0; continue; }
            int dx=u-p, dy=w-q, d=dx*dx+dy*dy;
            long c=0;
            /* apex v: x with |vx|^2 = d, x != y, x != 2v-y (collinear) */
            c += cntv[d] - 1;
            if(inside(2*p-u, 2*q-w)) c -= 1;
            /* apex y: x with |yx|^2 = d, x != v, x != 2y-v */
            long cy=0;
            for(int e=vhead[d]; e!=-1; e=vnext[e]){
                int X=u+vx[e], Y=w+vy_[e];
                if(inside(X,Y)) cy++;
            }
            cy -= 1;                              /* x = v */
            if(inside(2*u-p, 2*w-q)) cy -= 1;     /* collinear antipode */
            c += cy;
            /* apex x: x on perpendicular bisector, minus midpoint if lattice */
            long cb = bisector_count(p,q,u,w);
            if(((u+p)%2==0) && ((w+q)%2==0) && inside((u+p)/2,(w+q)/2)) cb -= 1;
            c += cb;
            if(c<0) c=0;
            codeg[idx]=(int)c; total+=c; if(c>mx) mx=(int)c;
        }
        /* tail counts */
        int tau = n/8; long Btau=0;
        for(int i=0;i<N;i++) if(codeg[i]>tau) Btau++;
        printf("(%3d,%3d)   %10lld %10.3f %10d %10.3f %10ld\n",
               p,q,total,(double)total/N,mx,(double)mx/n,Btau);
        if(vi==0){
            printf("   tail ladder for v=(%d,%d):  tau   B_v(tau)   B*tau/n^2   [claim <= 32]\n",p,q);
            for(double f=1.0; f>=0.02; f/=2.0){
                int t=(int)(f*n); if(t<1) break;
                long B=0; for(int i=0;i<N;i++) if(codeg[i]>t) B++;
                printf("   %28d %10ld %11.3f\n", t, B, (double)B*t/((double)N));
            }
            printf("   2D/N estimate (mean) = %.3f ;  1.75*2*ln n = %.3f\n",
                   (double)total/N, 3.5*logn);
        }
    }
    return 0;
}
