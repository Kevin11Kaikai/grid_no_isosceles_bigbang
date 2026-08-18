"""Numerically confirm the moment sums used in the alteration proofs:
   M_j(R) = sum_{r<=R} r_2(r)^j   where r_2(r)=#{(a,b) in Z^2: a^2+b^2=r}.
Theory: M_1 ~ pi R,  M_2 ~ 4 R log R,  M_j ~ c_j R (log R)^{2^{j-1}-1}."""
import numpy as np, math
for R in [10**4,10**5,10**6,4*10**6]:
    L=int(math.isqrt(R))
    cnt=np.zeros(R+1,np.int64)
    for a in range(-L,L+1):
        a2=a*a
        b=0
        while a2+b*b<=R:
            cnt[a2+b*b]+=1
            if b>0: cnt[a2+b*b]+=1
            b+=1
    c=cnt[1:].astype(np.float64)
    M1=c.sum(); M2=(c**2).sum(); M3=(c**3).sum(); M4=(c**4).sum()
    lg=math.log(R)
    print(f"R={R:9d}  M1/R={M1/R:7.4f}(pi={math.pi:.4f})  M2/(R lnR)={M2/(R*lg):7.4f}  "
          f"M3/(R lnR^3)={M3/(R*lg**3):8.5f}  M4/(R lnR^7)={M4/(R*lg**7):9.6f}  maxr2={int(c.max())}",flush=True)
