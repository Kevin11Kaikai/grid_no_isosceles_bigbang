import sys; sys.argv=['x']
exec(open('onecol2.py',encoding='utf-8').read().split('for n in [40')[0])
import time
for n in [96,112,128,160,192,224,256]:
    f,nd,t = solve(n, cap=40_000_000, seed=n, restarts=3)
    print("n=%4d  %-5s nodes=%-12d %.1fs" % (n,"FOUND" if f else "no",nd,t)); sys.stdout.flush()
    if f: open('onecol_n%d.txt'%n,'w').write(' '.join(map(str,f)))
