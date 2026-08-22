/* s8_proc.c -- run the random greedy independent set process on H_n and measure the
 * spread of d_2^+(v) = #{x : {v,x} became an edge of H(i) at some i <= m}.
 *
 * Purpose: test the prediction of Theorem 2 (THEOREM_AND_PROOF.md), namely that the
 * Bennett-Bohman pointwise condition d_2^+(v) in s_2^+ +/- o(s_2) is FALSE for H_n:
 * max_v d_2^+(v) should exceed mean_v d_2^+(v) by a factor 1 + c/(alpha log log n),
 * i.e. a large constant that decays only like 1/log log n.
 *
 * Also reports the survival ratio |A_v cap V(i)| / (q |A_v|) used as hypothesis
 * (H-surv) in Theorem 2, where A_v is v's column at even offset.
 *
 * This is a sanity check on a stated hypothesis and a prediction. It is not a proof.
 *
 * build: gcc -O2 -o s8_proc s8_proc.c -lm
 * run:   ./s8_proc <n> <alpha_num/100> <seed>       e.g. ./s8_proc 128 50 1
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

static int n, N, RMAX;
static int *vhead, *vnext, *vxa, *vxb;

static int igcd(int a,int b){ if(a<0)a=-a; if(b<0)b=-b; while(b){int t=a%b;a=b;b=t;} return a; }
static long long egcd(long long a,long long b,long long*x,long long*y){
    if(b==0){*x=1;*y=0;return a;} long long x1,y1,g=egcd(b,a%b,&x1,&y1);
    *x=y1;*y=x1-(a/b)*y1; return g; }
static int inside(int a,int b){ return a>=0&&a<n&&b>=0&&b<n; }

/* enumerate every x making {p,q},{u,w},x a NONDEGENERATE isosceles triple.
   writes indices into out[], returns count. out must have room for ~4n. */
static int enum_iso(int p,int q,int u,int w,int *out,int *cntc,int cap){
    int m=0;
    int dx=u-p, dy=w-q, d=dx*dx+dy*dy;
    if(d==0||d>RMAX) return 0;
    /* apex (p,q): |px|^2 = d */
    for(int e=vhead[d]; e!=-1; e=vnext[e]){
        int X=p+vxa[e], Y=q+vxb[e];
        if(!inside(X,Y)) continue;
        if(X==u&&Y==w) continue;                 /* x = y */
        if(X==2*p-u && Y==2*q-w) continue;       /* collinear antipode */
        if(m<cap) out[m++]=X*n+Y;
    }
    /* apex (u,w): |ux|^2 = d */
    for(int e=vhead[d]; e!=-1; e=vnext[e]){
        int X=u+vxa[e], Y=w+vxb[e];
        if(!inside(X,Y)) continue;
        if(X==p&&Y==q) continue;
        if(X==2*u-p && Y==2*w-q) continue;
        if(m<cap) out[m++]=X*n+Y;
    }
    /* apex x: x on perpendicular bisector, excluding the midpoint (collinear) */
    long long A=2*(long long)dx, B=2*(long long)dy;
    long long K=(long long)u*u+(long long)w*w-(long long)p*p-(long long)q*q;
    long long g=igcd((int)(A<0?-A:A),(int)(B<0?-B:B));
    if(g!=0 && K%g==0){
        long long a=A/g,b=B/g,c=K/g,s,t; egcd(a,b,&s,&t);
        long long x0=s*c,y0=t*c;
        double lo=-1e18,hi=1e18;
        if(b>0){double l=(double)(x0-(n-1))/b,h=(double)x0/b; if(l>lo)lo=l; if(h<hi)hi=h;}
        else if(b<0){double l=(double)x0/b,h=(double)(x0-(n-1))/b; if(l>lo)lo=l; if(h<hi)hi=h;}
        else if(x0<0||x0>n-1) goto donebis;
        if(a>0){double l=(double)(-y0)/a,h=(double)((n-1)-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h;}
        else if(a<0){double l=(double)((n-1)-y0)/a,h=(double)(-y0)/a; if(l>lo)lo=l; if(h<hi)hi=h;}
        else if(y0<0||y0>n-1) goto donebis;
        {
        long long klo=(long long)ceil(lo-1e-9), khi=(long long)floor(hi+1e-9);
        for(long long k=klo;k<=khi;k++){
            long long X=x0-b*k, Y=y0+a*k;
            if(X<0||X>=n||Y<0||Y>=n) continue;
            if(2*X==u+p && 2*Y==w+q) continue;   /* midpoint: collinear */
            if(m<cap) out[m++]=(int)(X*n+Y);
        }
        }
    }
donebis:
    *cntc=m; return m;
}

static unsigned long long rs;
static double urnd(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return (double)(rs>>11)/9007199254740992.0; }

int main(int argc,char**argv){
    n = argc>1?atoi(argv[1]):128;
    int alpha100 = argc>2?atoi(argv[2]):50;
    rs = argc>3?(unsigned long long)atoi(argv[3]):1ULL; rs = rs*2862933555777941757ULL+3037000493ULL;
    N=n*n; RMAX=2*(n-1)*(n-1);
    double alpha = alpha100/100.0;
    int m = (int)(alpha*n);

    vhead=malloc(sizeof(int)*(RMAX+1));
    for(int i=0;i<=RMAX;i++) vhead[i]=-1;
    int cap=(2*n-1)*(2*n-1);
    vnext=malloc(sizeof(int)*cap); vxa=malloc(sizeof(int)*cap); vxb=malloc(sizeof(int)*cap);
    int nv=0;
    for(int a=-(n-1);a<=n-1;a++)for(int b=-(n-1);b<=n-1;b++){
        if(!a&&!b) continue; int d=a*a+b*b; if(d>RMAX) continue;
        vxa[nv]=a; vxb[nv]=b; vnext[nv]=vhead[d]; vhead[d]=nv; nv++;
    }

    int *alive=malloc(sizeof(int)*N), *pos=malloc(sizeof(int)*N);
    char *dead=calloc(N,1);
    for(int i=0;i<N;i++){ alive[i]=i; pos[i]=i; }
    int nal=N;
    int *I=malloc(sizeof(int)*(m+2)); int ni=0;
    int obcap=8*n+64; int *ob=malloc(sizeof(int)*obcap); int obc;

    /* track survival of A_v for v = centre */
    int vc = (n/2)*n + (n/2);
    int vcx=n/2, vcy=n/2;
    int avtot=0; for(int k=-(n/2)/1;k<=n/2;k++){ if(k==0)continue; int Y=vcy+2*k; if(Y>=0&&Y<n) avtot++; }

    printf("n=%d N=%d alpha=%.2f m=%d\n", n,N,alpha,m);
    int steps=0;
    for(steps=0; steps<m && nal>0; steps++){
        int idx=(int)(urnd()*nal); if(idx>=nal) idx=nal-1;
        int y=alive[idx];
        /* remove y */
        int last=alive[--nal]; alive[idx]=last; pos[last]=idx; dead[y]=1;
        /* block everything closed by {a,y} for a in I */
        int yp=y/n, yq=y%n;
        for(int j=0;j<ni;j++){
            int a=I[j], ap=a/n, aq=a%n;
            enum_iso(ap,aq,yp,yq,ob,&obc,obcap);
            for(int k=0;k<obc;k++){
                int u=ob[k];
                if(dead[u]) continue;
                dead[u]=1; int pu=pos[u]; int lst=alive[--nal]; alive[pu]=lst; pos[lst]=pu;
            }
        }
        I[ni++]=y;
    }
    double q = (double)nal/N;
    /* A_v survival for the centre vertex */
    int avs=0; for(int k=-n;k<=n;k++){ if(k==0)continue; int Y=vcy+2*k; if(Y<0||Y>=n)continue;
        if(!dead[vcx*n+Y]) avs++; }

    /* d_2^+(v) for all v : #{x : exists a in I with {v,x,a} isosceles} */
    int *stamp=calloc(N,sizeof(int)); int sc=0;
    long long tot=0; int mx=0, mxv=-1;
    int *hist=calloc(4096,sizeof(int));
    for(int v=0;v<N;v++){
        int vp=v/n, vq=v%n; sc++;
        int cnt=0;
        for(int j=0;j<ni;j++){
            int a=I[j]; if(a==v) continue;
            enum_iso(vp,vq,a/n,a%n,ob,&obc,obcap);
            for(int k=0;k<obc;k++){ int x=ob[k]; if(x==v) continue;
                if(stamp[x]!=sc){ stamp[x]=sc; cnt++; } }
        }
        tot+=cnt; if(cnt>mx){mx=cnt;mxv=v;}
        int h=cnt; if(h>4095)h=4095; hist[h]++;
    }
    double mean=(double)tot/N;
    /* count vertices above 1.5x and 2x the mean */
    int a15=0,a20=0;
    for(int h=0;h<4096;h++){ if(h>1.5*mean) a15+=hist[h]; if(h>2.0*mean) a20+=hist[h]; }
    printf("steps=%d  |I|=%d  |V(m)|=%d  q=%.4f\n", steps, ni, nal, q);
    printf("A_v(centre): %d/%d survive = %.4f   (q=%.4f, ratio %.3f)\n",
           avs, avtot, avtot?(double)avs/avtot:0.0, q, (avtot&&q>0)?((double)avs/avtot)/q:0.0);
    printf("d_2^+:  mean=%.2f  max=%.0f  max/mean=%.3f   #{>1.5mean}=%d  #{>2mean}=%d\n",
           mean,(double)mx,mx/mean,a15,a20);
    printf("        Delta_2 ~ n = %d ; excess (max-mean)/n = %.3f ; predicted g ~ 2ln n/lnln n = %.2f\n",
           n, (mx-mean)/n, 2*log((double)n)/log(log((double)n)));
    return 0;
}
