"""exact r_3(n) with incremental lower-bound seeding; writes r3.txt"""
import sys, time
sys.path.insert(0,'D:/Others/iso6/routes/D')

def r3(n, lb=0):
    best=[lb]; bestS=[[]]
    full=(1<<n)-1
    def dfs(i, chosen, cl, banned):
        avail=(~banned)&full&~((1<<i)-1)
        if chosen+bin(avail).count('1')<=best[0]: return
        if avail==0:
            if chosen>best[0]: best[0]=chosen; bestS[0]=list(cl)
            return
        j=(avail&-avail).bit_length()-1
        nb=banned|(1<<j)
        for a in cl:
            c=2*j-a
            if c<n: nb|=(1<<c)
        cl.append(j); dfs(j+1,chosen+1,cl,nb); cl.pop()
        dfs(j+1,chosen,cl,banned|(1<<j))
    dfs(0,0,[],0)
    return best[0], bestS[0]

if __name__=='__main__':
    hi=int(sys.argv[1]) if len(sys.argv)>1 else 70
    lb=0; out=[]
    f=open('D:/Others/iso6/routes/D/r3.txt','w')
    for n in range(1,hi+1):
        t=time.time()
        v,S=r3(n,lb=lb-1)   # lb-1 so that a set of size lb is still recorded
        if v<lb: v=lb
        lb=v
        line=f"{n} {v} {time.time()-t:.1f}"
        print(line,flush=True); f.write(line+"\n"); f.flush()
    f.close()
