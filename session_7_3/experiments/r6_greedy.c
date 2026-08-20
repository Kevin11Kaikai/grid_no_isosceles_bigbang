/* Round 6, probe 6.1 -- random greedy independent set in the isosceles hypergraph
 * on [n]^2, pushed far enough to distinguish  Theta(n)  from  Theta(n/sqrt(log n)).
 *
 * Exactly the process arXiv:2601.14465 says "most probably" gives a linear bound.
 * Vertices in uniformly random order; accept p iff S u {p} stays isosceles-free,
 * i.e. for every already-chosen s_i:  |p-s_i|^2 not already a distance at apex s_i,
 * and the |p-s_i|^2 are pairwise distinct (that is the apex-p condition).
 * Degenerate/collinear triples are caught by the apex-midpoint case, as required.
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

static uint64_t rs;
static inline uint64_t rnd64(void){ rs^=rs<<13; rs^=rs>>7; rs^=rs<<17; return rs; }

static uint32_t CAP, MASK;
static uint32_t **rows;                 /* rows[i] = open-addressed set of distances at apex i */
static uint32_t *tkey, *tstamp, tcur;   /* scratch set for the apex-p condition */

static inline int row_has(uint32_t i, uint32_t d){
    uint32_t h = (d*2654435761u) & MASK, *r = rows[i];
    while (r[h]) { if (r[h]==d) return 1; h = (h+1)&MASK; }
    return 0;
}
static inline void row_add(uint32_t i, uint32_t d){
    uint32_t h = (d*2654435761u) & MASK, *r = rows[i];
    while (r[h]) { if (r[h]==d) return; h = (h+1)&MASK; }
    r[h] = d;
}
static inline int scr_has_add(uint32_t d){
    uint32_t h = (d*2654435761u) & MASK;
    while (tstamp[h]==tcur) { if (tkey[h]==d) return 1; h = (h+1)&MASK; }
    tstamp[h]=tcur; tkey[h]=d; return 0;
}

int main(int argc, char **argv){
    int n = atoi(argv[1]);
    rs = strtoull(argv[2], NULL, 10) | 1;
    long N = (long)n*n;
    /* CAP: load factor <= ~0.5 for m up to ~1.6n */
    uint32_t want = (uint32_t)(3.4*n) + 16, c = 1024;
    while (c < want) c <<= 1;
    CAP = c; MASK = c-1;

    int32_t *px = malloc(N*4), *py = malloc(N*4);
    for (long i=0;i<N;i++){ px[i]=i%n; py[i]=i/n; }
    for (long i=N-1;i>0;i--){                       /* uniform shuffle */
        long j = rnd64()%(i+1);
        int32_t t=px[i]; px[i]=px[j]; px[j]=t;
        t=py[i]; py[i]=py[j]; py[j]=t;
    }
    uint32_t mmax = (uint32_t)(2.0*n)+64;
    rows = malloc(sizeof(uint32_t*)*mmax);
    int32_t *sx = malloc(mmax*4), *sy = malloc(mmax*4);
    tkey = malloc(CAP*4); tstamp = calloc(CAP,4); tcur = 0;

    uint32_t m = 0;
    for (long k=0;k<N;k++){
        int32_t X=px[k], Y=py[k];
        tcur++;
        if (tcur==0){ memset(tstamp,0,CAP*4); tcur=1; }
        int ok = 1; uint32_t i;
        for (i=0;i<m;i++){
            int32_t dx=X-sx[i], dy=Y-sy[i];
            uint32_t d = (uint32_t)(dx*dx + dy*dy);
            if (row_has(i,d)) { ok=0; break; }
            if (scr_has_add(d)) { ok=0; break; }
        }
        if (!ok) continue;
        if (m+1 >= mmax || m+1 >= CAP/2){ fprintf(stderr,"CAP/mmax too small at m=%u\n",m); return 2; }
        rows[m] = calloc(CAP,4);
        for (i=0;i<m;i++){
            int32_t dx=X-sx[i], dy=Y-sy[i];
            uint32_t d = (uint32_t)(dx*dx + dy*dy);
            row_add(i,d); row_add(m,d);
        }
        sx[m]=X; sy[m]=Y; m++;
    }
    printf("%d %u\n", n, m);
    return 0;
}
