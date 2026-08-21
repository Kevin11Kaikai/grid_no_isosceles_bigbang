/* Round 11 -- the exact degree profile of H_n.
 *
 * BB Thm 1.1 requires H to be D-REGULAR.  Round 6 measured Dmax/Davg ~ 1.47 and the
 * campaign has never looked at it again.  This computes the profile exactly.
 *
 * Every edge of H_n has a UNIQUE apex: two apexes would force an equilateral triangle,
 * which does not exist in Z^2.  So for a in [n]^2,
 *
 *    deg(a) = #{ {b,c} : |ab| = |ac| }                     (a is the apex)
 *           + sum_{x != a} ( N_x(|xa|^2) - 1 )             (x is the apex, a a base pt)
 *
 * where N_x(r) = #grid points at squared distance r from x.  Both terms come out of one
 * loop over the apex x: bucket the grid by squared distance from x, then for every a,
 * cnt[r(a)]-1 is what a receives, and half the sum of those is x's own apex degree.
 * O(N^2) total, no multiplicity factor.
 *
 * gcc -O2 -o r11_reg r11_reg.c -lm
 * usage: r11_reg <n>
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>

int main(int argc, char **argv){
    int n = argc>1?atoi(argv[1]):64;
    long N = (long)n*n;
    int RMAX = 2*(n-1)*(n-1);

    int *cnt = malloc((size_t)(RMAX+1)*sizeof(int));
    long long *deg = calloc((size_t)N, sizeof(long long));
    int *px = malloc((size_t)N*sizeof(int));
    int *py = malloc((size_t)N*sizeof(int));
    for(long i=0;i<N;i++){ px[i]=(int)(i%n); py[i]=(int)(i/n); }

    for(long x=0;x<N;x++){
        memset(cnt,0,(size_t)(RMAX+1)*sizeof(int));
        int xx=px[x], xy=py[x];
        for(long a=0;a<N;a++){
            if(a==x) continue;
            int dx=px[a]-xx, dy=py[a]-xy;
            cnt[dx*dx+dy*dy]++;
        }
        long long apex=0;
        for(long a=0;a<N;a++){
            if(a==x) continue;
            int dx=px[a]-xx, dy=py[a]-xy;
            int c = cnt[dx*dx+dy*dy]-1;   /* partners of a at the same distance from x */
            apex += c;                    /* counts ordered pairs -> halve below */
            deg[a] += c;                  /* a is a base vertex of an x-apex edge */
        }
        deg[x] += apex/2;                 /* x as apex: sum_r C(m_r,2) */
    }

    long long mn=deg[0], mx=deg[0], tot=0;
    long amn=0, amx=0;
    for(long a=0;a<N;a++){
        tot += deg[a];
        if(deg[a]<mn){ mn=deg[a]; amn=a; }
        if(deg[a]>mx){ mx=deg[a]; amx=a; }
    }
    double avg = (double)tot/(double)N;
    long ctr = (long)(n/2)*n + n/2;
    long cor = 0;
    long mid = (long)(n/2)*n + 0;          /* middle of the left edge */

    printf("n=%d  N=%ld  |E| = %lld\n", n, N, tot/3);
    printf("  Davg = %.1f   = %.4f n^2 ln n\n", avg, avg/((double)N*log((double)n)));
    printf("  Dmin = %lld  at (%d,%d)\n", mn, px[amn], py[amn]);
    printf("  Dmax = %lld  at (%d,%d)\n", mx, px[amx], py[amx]);
    printf("  Dmax/Dmin = %.4f    Dmax/Davg = %.4f    Davg/Dmin = %.4f\n",
           (double)mx/(double)mn, (double)mx/avg, avg/(double)mn);
    printf("  centre (%d,%d) = %lld (%.4f Davg) | corner (0,0) = %lld (%.4f) | edge-mid = %lld (%.4f)\n",
           n/2,n/2, deg[ctr], deg[ctr]/avg, deg[cor], deg[cor]/avg, deg[mid], deg[mid]/avg);
    /* how much mass has to be added to regularise upward to Dmax */
    double add=0; for(long a=0;a<N;a++) add += (double)(mx-deg[a]);
    printf("  dummy edges needed to reach Dmax-regular: %.0f incidences = %.4f of |E|\n",
           add/3.0, (add/3.0)/((double)(tot/3)));
    return 0;
}
