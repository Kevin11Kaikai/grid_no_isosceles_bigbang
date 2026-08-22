/* s8_joint.c -- the joint statistic that decides the correlation obligation.
 *
 * A(v,y) := sum_u codeg(v,u) * codeg(u,y)     (u ranges over the grid)
 *
 * This is the one-step jump of the master statistic
 *     W(v,i) = sum_u codeg(v,u) * e(u,i),     e(u,i) = d_2^+(u,i) - s_2^+(t_i),
 * whose control is exactly obligation (Q) of Session 8's HANDOFF.
 *
 * Analytic prediction (Lemma D, THEOREM_AND_PROOF Part V):
 *     A(v,y)  =  Theta( n^2 log^2 n  +  (n / s(v,y))^3 ),
 * where s(v,y) is the sup-norm of the primitive direction of y - v; hence
 *     #{ y : A(v,y) > lambda }  =  O( n^2 / lambda^{1/3} )   for lambda >= n^2 log^2 n,
 *     max_y A(v,y)              =  Theta( n^3 ).
 * The competing possibility -- positive clustering, i.e. A(v,y) >> n^3 for some y, or a
 * tail heavier than lambda^{-1/3} -- would refute Lemma C.
 *
 * Computes the full N x N codegree matrix, so cost is O(n^4 log n) time, O(n^4) memory
 * as uint16.  n <= 64 comfortably.
 *
 * build: gcc -O2 -o s8_joint s8_joint.c -lm
 * run:   ./s8_joint <n>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N, RMAX;
static int *vhead, *vnext, *vxa, *vxb;
static int *cntv;

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

/* codeg(v=(p,q), y=(u,w)) */
static int codeg_pair(int p,int q,int u,int w){
    if(p==u&&q==w) return 0;
    int dx=u-p,dy=w-q,d=dx*dx+dy*dy;
    long c=0;
    c += cntv[d] - 1;                                   /* apex v (cntv is centred at v) */
    if(inside(2*p-u,2*q-w)) c -= 1;
    long cy=0;
    for(int e=vhead[d]; e!=-1; e=vnext[e]){
        int X=u+vxa[e],Y=w+vxb[e]; if(inside(X,Y)) cy++;
    }
    cy -= 1; if(inside(2*u-p,2*w-q)) cy -= 1;
    c += cy;
    long cb = bisector_count(p,q,u,w);
    if(((u+p)%2==0)&&((w+q)%2==0)&&inside((u+p)/2,(w+q)/2)) cb -= 1;
    c += cb;
    return c<0?0:(int)c;
}

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):48;
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
    cntv=malloc(sizeof(int)*(RMAX+1));

    unsigned short *Cg = malloc((size_t)N*N*sizeof(unsigned short));
    if(!Cg){ printf("alloc fail\n"); return 1; }
    for(int a=0;a<N;a++){
        int p=a/n,q=a%n;
        memset(cntv,0,sizeof(int)*(RMAX+1));
        for(int x=0;x<n;x++)for(int y2=0;y2<n;y2++){
            int dx=x-p,dy=y2-q; if(!dx&&!dy) continue; cntv[dx*dx+dy*dy]++;
        }
        for(int b=0;b<N;b++) Cg[(size_t)a*N+b]=(unsigned short)codeg_pair(p,q,b/n,b%n);
    }

    /* v = centre */
    int vp=n/2, vq=n/2, v=vp*n+vq;
    double logn=log((double)n);
    double *A=malloc(sizeof(double)*N);
    for(int y=0;y<N;y++){
        if(y==v){ A[y]=0; continue; }
        double s=0;
        const unsigned short *cv=Cg+(size_t)v*N, *cy=Cg+(size_t)y*N;
        for(int u=0;u<N;u++) s += (double)cv[u]*cy[u];
        A[y]=s;
    }
    double n3=(double)n*n*n, n2l2=(double)n*n*logn*logn;
    double mx=0; int mxy=-1; double tot=0;
    for(int y=0;y<N;y++){ if(A[y]>mx){mx=A[y];mxy=y;} tot+=A[y]; }
    printf("n=%d N=%d  v=(%d,%d)\n",n,vp,vq,n);
    printf("  max_y A = %.4g   max/n^3 = %.4f   (mxy=(%d,%d), s(v,y)=%d)\n",
           mx, mx/n3, mxy/n, mxy%n,
           igcd(abs(mxy/n-vp),abs(mxy%n-vq))?
             ( (abs(mxy/n-vp)>abs(mxy%n-vq)?abs(mxy/n-vp):abs(mxy%n-vq))
               / igcd(abs(mxy/n-vp),abs(mxy%n-vq)) ) : 0);
    printf("  mean_y A = %.4g   mean/(n^2 log^2 n) = %.4f\n", tot/N, (tot/N)/n2l2);
    /* the one-step jump of W is the CENTRED statistic A(v,y) - mean_y A(v,.) */
    double mean=tot/N, v2=0;
    for(int y=0;y<N;y++){ double z=A[y]-mean; v2+=z*z; }
    v2/=N;
    printf("  centred jump J(y)=A-mean:  sd/n^3=%.4f   max/n^3=%.4f   sd/(n^2 log^2 n)=%.4f\n",
           sqrt(v2)/n3, (mx-mean)/n3, sqrt(v2)/n2l2);
    printf("  tail of centred jump:  thr/n^3    #{J>thr}      frac    #{J>thr}/n\n");
    for(double f=2.0; f>=0.03; f/=1.5){
        double thr=f*n3; long c=0; for(int y=0;y<N;y++) if(A[y]-mean>thr) c++;
        printf("        %19.4f %10ld %10.5f %11.3f\n", f, c, (double)c/N, (double)c/n);
    }
    /* correlation diagnostic: A(v,y) vs (n/s(v,y))^3 */
    printf("  by s(v,y):   s    count      mean A      (n/s)^3     ratio\n");
    for(int s=1;s<=8;s++){
        double sum=0; long c=0;
        for(int y=0;y<N;y++){
            if(y==v) continue;
            int dx=y/n-vp, dy=y%n-vq; int g=igcd(abs(dx),abs(dy)); if(g==0) continue;
            int a=abs(dx)/g, b=abs(dy)/g; int ss=a>b?a:b;
            if(ss==s){ sum+=A[y]; c++; }
        }
        if(c) printf("            %3d %8ld %11.4g %12.4g %9.3f\n",
                     s,c,sum/c,pow((double)n/s,3.0),(sum/c)/pow((double)n/s,3.0));
    }
    return 0;
}
