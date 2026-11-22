import os, json, sys, numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
spec = json.load(open(sys.argv[1]))
k = Kokoro('models/kokoro-v1.0.onnx', 'models/voices-v1.0.bin')
SR = 24000
gap = int(0.18*SR)
chunks=[]; t=0.0; out=[]
for i,l in enumerate(spec['lines']):
    samples, sr = k.create(l['say'], voice=spec['voice'], speed=spec['speed'], lang='en-us')
    assert sr==SR
    # trim trailing silence a bit
    thr = 0.01
    idx = np.where(np.abs(samples)>thr)[0]
    samples = samples[:idx[-1]+int(0.05*SR)] if len(idx) else samples
    dur = len(samples)/SR
    words = l['show'].split()
    weights = np.array([len(w)+ (4 if w[-1] in '.,:' else 0) for w in words], float)
    cum = np.concatenate([[0],np.cumsum(weights)])/weights.sum()
    ws = [{"w":w,"s":round(t+dur*cum[j],3),"e":round(t+dur*cum[j+1],3)} for j,w in enumerate(words)]
    out.append({**l,"start":round(t,3),"end":round(t+dur,3),"words":ws})
    chunks.append(samples); chunks.append(np.zeros(gap,dtype=np.float32))
    t += dur + gap/SR
audio = np.concatenate(chunks)
os.makedirs('video/public',exist_ok=True)
sf.write(f"video/public/{spec['id']}.wav", audio, SR)
total = len(audio)/SR
json.dump({"id":spec['id'],"duration":round(total,3),"lines":out}, open(f"video/public/{spec['id']}.json","w"), indent=1)
print("duration", total)
for o in out: print(o['start'], o['end'], o['show'])
