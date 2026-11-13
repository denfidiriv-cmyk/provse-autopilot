import json,subprocess,sys,os
proj,tempo,cutidx,ids,lib=sys.argv[1],float(sys.argv[2]),json.loads(sys.argv[3]),sys.argv[4].split(','),sys.argv[5]
os.chdir(proj)
w=json.load(open('wordtimes.json'))
if tempo!=1.0:
    subprocess.run(['ffmpeg','-y','-loglevel','error','-i','vt.wav','-af',f'atempo={tempo}','vt_t.wav'],check=True)
    w=[[a,t/tempo] for a,t in w]; json.dump(w,open('wordtimes_t.json','w'),ensure_ascii=False)
else:
    subprocess.run(['cp','vt.wav','vt_t.wav'],check=True); json.dump(w,open('wordtimes_t.json','w'),ensure_ascii=False)
VO=0.2; T=[round(t+VO,3) for _,t in w]; C=lambda i: round(T[i]-0.08,3)
dur=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0','vt_t.wav']))
END=round(dur+VO+1.6,2)
cuts=[0]+[C(i) for i in cutidx]+[END]
eras=[{'id':i,'dur':round(cuts[k+1]-cuts[k],3),'counter':False} for k,i in enumerate(ids)]
d='代码工程/scenes_x'; os.makedirs(d,exist_ok=True)
open(f'{d}/_wt.js','w').write('window.WT='+json.dumps(T)+';\nwindow.CUTS='+json.dumps(cuts)+';\n')
open(f'代码工程/eras_{os.path.basename(proj)}film.js','w').write("window.FILM_SIZE=[1080,1920];\nwindow.SCENE_DIR='scenes_x';\nwindow.SCENE_LIBS=['scenes_x/_wt.js','scenes_x/"+lib+"'];\nwindow.ERAS="+json.dumps(eras)+";\n")
open('END.txt','w').write(str(END))
print('END',END,[round(cuts[k+1]-cuts[k],2) for k in range(len(ids))])
