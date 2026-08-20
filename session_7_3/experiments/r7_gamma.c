/* Round 7, probe 7.2 -- Gamma(H_n) exactly, per Bennett-Bohman's definition
 * (lit/ind.tex lines 250-253): Gamma = max over distinct v,v' of the number of
 * edge pairs e,e' with v in e\e', v' in e'\e, |e n e'| = r-1 = 2.
 * For r=3 that is: #pairs {a,b} forming an isosceles triple with BOTH v and v'.
 *
 * Round 1 found the extremal pairs are axis-parallel. Evaluate at the central
 * same-row pair, and compare against random pairs to confirm it is the max.
 */
#include <stdio.h>
#include <stdlib.h>
static int n;
static inline int iso(int vx,int vy,int ax,int ay,int bx,int by){
    long dva=(long)(vx-ax)*(vx-ax)+(long)(vy-ay)*(vy-ay);
    long dvb=(long)(vx-bx)*(vx-bx)+(long)(vy-by)*(vy-by);
    long dab=(long)(ax-bx)*(ax-bx)+(long)(ay-by)*(ay-by);
    return (dva==dvb)||(dva==dab)||(dvb==dab);
}
static long count(int vx,int vy,int wx,int wy){
    long N=(long)n*n, tot=0;
    for(long i=0;i<N;i++){
        int ax=i%n, ay=i/n;
        if((ax==vx&&ay==vy)||(ax==wx&&ay==wy)) continue;
        for(long j=i+1;j<N;j++){
            int bx=j%n, by=j/n;
            if((bx==vx&&by==vy)||(bx==wx&&by==wy)) continue;
            if(iso(vx,vy,ax,ay,bx,by) && iso(wx,wy,ax,ay,bx,by)) tot++;
        }
    }
    return tot;
}
int main(int argc,char**argv){
    n=atoi(argv[1]);
    int c=n/2;
    long row = count(0,c, n-1,c);          /* same row, spanning */
    long col = count(c,0, c,n-1);          /* same column */
    long diag= count(0,0, n-1,n-1);        /* diagonal pair */
    long gen = count(1,2, n-3,c+1);        /* generic pair */
    printf("%4d  row=%-10ld col=%-10ld diag=%-9ld generic=%-9ld  row/n^2=%.4f\n",
           n,row,col,diag,gen,(double)row/((double)n*n));
    return 0;
}
