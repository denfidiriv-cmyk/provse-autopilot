import sherpa_onnx, wave, numpy as np, json, glob, sys
d=glob.glob('sherpa-onnx-nemo-*')[0]
r=sherpa_onnx.OfflineRecognizer.from_transducer(encoder=f'{d}/encoder.int8.onnx',decoder=f'{d}/decoder.int8.onnx',joiner=f'{d}/joiner.int8.onnx',tokens=f'{d}/tokens.txt',model_type='nemo_transducer',num_threads=4)
w=wave.open(sys.argv[1]);sr=w.getframerate();a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
# chunk at 20s windows to keep memory sane
out=[];step=len(a)+1;i=0
while i<len(a):
    s=r.create_stream();s.accept_waveform(sr,a[i:i+step]);r.decode_stream(s)
    res=s.result
    for t,ts in zip(res.tokens,res.timestamps): out.append([t,ts+i/sr])
    i+=step
json.dump(out,open('tok.json','w'),ensure_ascii=False)
print(''.join(t for t,_ in out).replace('▁',' '))
