import math, json, os
sk={1:{8:10,11:13,16:19,22:27,32:36,45:51,64:70,90:100,128:140,181:191,256:268},
    2:{8:21,11:30,16:42,22:64,32:96,45:139,64:212,90:307,128:474,181:713,256:1076},
    3:{32:155,45:242,64:374,90:575,128:917,181:1414}}
print("Local log-log slopes d log(size)/d log(n)  (predicted asymptote 2-2/(k+1)):")
for k in sk:
    ns=sorted(sk[k]); pred=2-2/(k+1)
    s=[]
    for a,b in zip(ns[:-1],ns[1:]):
        s.append(f"{a}->{b}:{math.log(sk[k][b]/sk[k][a])/math.log(b/a):.3f}")
    print(f" k={k} (pred {pred:.3f}): "+"  ".join(s))
print()
print("Ratios D(k)/D(1):")
for n in [11,16,32,64,90,128,181,256]:
    r2=sk[2].get(n,0)/sk[1][n] if n in sk[2] else None
    r3=sk[3].get(n,0)/sk[1][n] if n in sk[3] else None
    print(f"  n={n:4d}  D2/D1={r2 if r2 is None else round(r2,2)}   D3/D1={r3 if r3 is None else round(r3,2)}")
print()
known={1:1,2:2,3:4,4:6,5:7,6:9,7:10,8:13,9:16,10:18,11:18,16:28,27:48,32:56}
print("KNOWN EXACT C(n): fits")
print(f"{'n':>4} {'C':>4} {'C/n':>7} {'C/(n/sqrt(ln n))':>18} {'C/(n^1.1)':>10}")
for n in sorted(known):
    if n<3: continue
    C=known[n]
    print(f"{n:>4} {C:>4} {C/n:7.3f} {C/(n/math.sqrt(math.log(n))):18.3f} {C/n**1.1:10.3f}")
print()
print("doubling ratios from exact values:")
for n in [3,4,5,8,16]:
    if 2*n in known: print(f"  C({2*n})/C({n}) = {known[2*n]}/{known[n]} = {known[2*n]/known[n]:.3f}   log2 = {math.log2(known[2*n]/known[n]):.3f}")
