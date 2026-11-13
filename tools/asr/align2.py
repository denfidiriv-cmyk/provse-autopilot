import json,re,difflib,sys
tok=json.load(open(sys.argv[1])); script=open(sys.argv[2]).read().split()
aw=[]
for t,ts in tok:
    if t.startswith(' ') or not aw: aw.append([t.strip(),ts])
    else: aw[-1][0]+=t
norm=lambda w:re.sub(r"[^\wʼ'’]","",w.lower()).replace('<unk>','')
A=[norm(w) for w,_ in aw]; S=[norm(w) for w in script]
# character-level mapping: map each script word start char to asr char positions
sa=''.join(S); aa=''.join(A)
sm=difflib.SequenceMatcher(None,sa,aa,autojunk=False)
amap={}
for b in sm.get_matching_blocks():
    for k in range(b.size): amap[b.a+k]=b.b+k
# asr char -> time (word start time, interpolate inside word by char share up to next word)
ct=[]
for i,(w,t) in enumerate(aw):
    n=len(A[i]); tn=aw[i+1][1] if i+1<len(aw) else t+0.4
    for k in range(n): ct.append(t+(tn-t)*k/max(n,1)*0.6)
out=[];pos=0
for w,s in zip(script,S):
    t=None
    for k in range(len(s)):
        if pos+k in amap: t=ct[amap[pos+k]]-0.0; t-= (k*0.06); break
    out.append([w,t]); pos+=len(s)
# interpolate missing
for i,(w,t) in enumerate(out):
    if t is None:
        j=i
        while j<len(out) and out[j][1] is None: j+=1
        a=out[i-1][1] if i else 0; b=out[j][1] if j<len(out) else a+0.5
        for k in range(i,j): out[k][1]=a+(b-a)*(k-i+1)/(j-i+1)
# monotonic
for i in range(1,len(out)): out[i][1]=max(out[i][1],out[i-1][1]+0.05)
json.dump([[w,round(t,3)] for w,t in out],open(sys.argv[3],'w'),ensure_ascii=False)
old=json.load(open(sys.argv[4]))
for (w,t),(_,o) in list(zip(out,old))[::12]: print(f'{w:15s} new {t:6.2f} old {o:6.2f}')
