import json,re,sys,numpy as np
from scipy.io import wavfile
raw,out_wav,words_f,out_json=sys.argv[1:5]
sr,x=wavfile.read(raw); xf=x.astype(float)/32768
h=int(sr*0.01); n=len(x)//h
db=20*np.log10(np.array([np.sqrt(np.mean(xf[i*h:(i+1)*h]**2)) for i in range(n)])+1e-9)
on=db>-30; segs=[];i=0
while i<n:
    if on[i]:
        j=i
        while j<n and (on[j] or on[j:j+12].any()): j+=1
        if (j-i)*0.01>0.08: segs.append((i*0.01,j*0.01))
        i=j
    else: i+=1
# tighten
MAXG=0.28;pad=0.03;parts=[np.zeros(int(0.05*sr),dtype=x.dtype)];t=0.05;prev=None;ns=[]
for a,b in segs:
    a0=max(0,a-pad);b0=min(len(x)/sr,b+pad)
    if prev is not None:
        g=min(max(0,a0-prev),MAXG); parts.append(x[int(prev*sr):int((prev+g)*sr)]); t+=g
    parts.append(x[int(a0*sr):int(b0*sr)]); ns.append((t+(a-a0),t+(a-a0)+(b-a))); t+=b0-a0; prev=b0
y=np.concatenate(parts); wavfile.write(out_wav,sr,y)
segs=ns
words=open(words_f).read().split()
V='аеєиіїоуюяАЕЄИІЇОУЮЯ'
LAT={'АТБ,':3}
def syl(w): return LAT.get(w, max(1,sum(c in V for c in w)))
ws=np.array([syl(w) for w in words],float)
D=np.array([b-a for a,b in segs]); rate=D.sum()/ws.sum()
W=len(words);S=len(segs);cs=np.concatenate([[0],np.cumsum(ws)])
INF=1e18;dp=np.full((S+1,W+1),INF);bk=np.zeros((S+1,W+1),int);dp[0][0]=0
for j in range(1,S+1):
    for k in range(0,W+1):
        best=INF;arg=-1
        # empty segment (noise)
        if dp[j-1][k]<INF:
            c=dp[j-1][k]+(D[j-1]**2)*3; best,arg=c,k
        for i in range(max(0,k-14),k):
            if dp[j-1][i]>=INF: continue
            c=dp[j-1][i]+(D[j-1]-rate*(cs[k]-cs[i]))**2
            if c<best: best,arg=c,i
        dp[j][k]=best;bk[j][k]=arg
k=W;assign=[]
for j in range(S,0,-1):
    i=bk[j][k];assign.append((j-1,i,k));k=i
assign.reverse();res=[None]*W
for j,i,k in assign:
    if k<=i: continue
    a,b=segs[j];tot=cs[k]-cs[i]
    for q in range(i,k): res[q]=[words[q],round(a+(cs[q]-cs[i])/tot*(b-a),3)]
json.dump(res,open(out_json,'w'),ensure_ascii=False)
print('dur',len(y)/sr,'segs',S,'words',W,'missing',sum(r is None for r in res))
for w,tt in res:
    if w[0].isupper(): print(tt,w)
