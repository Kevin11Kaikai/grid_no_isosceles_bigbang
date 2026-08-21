/* Round 6, probe 6.2 -- does the Bennett-Bohman CONCLUSION hold for H_n although
 * its HYPOTHESES fail (Round 1)?
 *
 * Sum_d N_a(d)^2 exactly (4-fold symmetry), then
 *    #edges = Sum_a [ Sum_d N_a(d)^2 - (N-1) ] / 2 ,   D = 3*#edges/N,
 * and the BB Thm 1.1 conclusion for r=3 is  |I| = Theta( N (ln N / D)^{1/2} ).
 */
#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <stdint.h>
int main(int argc,char**argv){
    int n=atoi(argv[1]);
    long N=(long)n*n;
    long maxd=2L*(n-1)*(n-1)+1;
    uint32_t *cnt=calloc(maxd,4);
    double total=0.0;
    int h=n/2;
    for(int ax=0;ax<h;ax++)for(int ay=0;ay<h;ay++){
        double s=0;
        for(int bx=0;bx<n;bx++){
            long dx=(long)ax-bx, dx2=dx*dx;
            for(int by=0;by<n;by++){
                if(bx==ax&&by==ay) continue;
                long dy=(long)ay-by; long d=dx2+dy*dy;
                s += 2.0*cnt[d]+1.0; cnt[d]++;
            }
        }
        for(int bx=0;bx<n;bx++){
            long dx=(long)ax-bx, dx2=dx*dx;
            for(int by=0;by<n;by++){
                if(bx==ax&&by==ay) continue;
                cnt[dx2+((long)ay-by)*((long)ay-by)]=0;
            }
        }
        total += 4.0*s;
    }
    double edges=(total-(double)N*(N-1))/2.0;
    double D=3.0*edges/(double)N;
    double bb=(double)N*sqrt(log((double)N)/D);
    printf("%5d  SumN2/(n^2 ln n)=%8.4f  D/(n^2 ln n)=%8.4f  BB=%10.1f  BB/n=%6.4f\n",
           n, total/((double)N*log((double)n)), D/((double)N*log((double)n)), bb, bb/n);
    return 0;
}
