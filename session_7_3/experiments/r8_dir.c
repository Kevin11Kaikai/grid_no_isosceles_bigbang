/* Round 8, probe 8.2 -- Gamma as a function of the DIRECTION of v-v'.
 * Prediction: Gamma = Theta(n^2) exactly when the reflection across the perpendicular
 * bisector of {v,v'} preserves Z^2, i.e. when the primitive direction (p,q) has
 * p^2+q^2 in {1,2}  ->  row (1,0), column (0,1), diagonal (1,1), anti-diagonal (1,-1).
 * For every other direction the mirror of a lattice point is not a lattice point, so the
 * both-apex family is empty and Gamma should collapse to the generic level.
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
            if(iso(vx,vy,ax,ay,bx,by)&&iso(wx,wy,ax,ay,bx,by)) tot++;
        }
    }
    return tot;
}
int main(int argc,char**argv){
    n=atoi(argv[1]);
    int dirs[][2]={{1,0},{0,1},{1,1},{1,-1},{2,1},{1,2},{2,-1},{3,1},{3,2},{5,1},{1,3},{4,1}};
    int nd=sizeof(dirs)/sizeof(dirs[0]);
    printf("n=%d   direction (p,q)  p^2+q^2  reflect-integral?   Gamma   Gamma/n^2\n",n);
    for(int k=0;k<nd;k++){
        int p=dirs[k][0], q=dirs[k][1], r=p*p+q*q;
        /* place v,v' symmetric about the centre, separated by m*(p,q) */
        int m=1; while(1){ int t=m+1;
            int cx=n/2-(t*p)/2, cy=n/2-(t*q)/2, dx=cx+t*p, dy=cy+t*q;
            if(cx<0||cy<0||dx>=n||dy>=n||cx>=n||cy>=n||dx<0||dy<0) break; m=t; }
        int vx=n/2-(m*p)/2, vy=n/2-(m*q)/2, wx=vx+m*p, wy=vy+m*q;
        long g=count(vx,vy,wx,wy);
        printf("        (%2d,%2d)  %7d  %-17s %7ld   %.4f\n",
               p,q,r,(r==1||r==2)?"YES":"no",g,(double)g/((double)n*n));
    }
    return 0;
}
