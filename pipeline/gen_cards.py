"""Render unique 1080x1350 image cards. Usage: python3 gen_cards.py cards.json outdir
cards.json: [{"id":"anthropic-ipo","kicker":"Anthropic IPO","big":"+34%","sub":"first day as a public company","source":"Source: Bloomberg","color":"#3DDC97"}, ...]
Writes outdir/<id>.png for each card. Needs the HyperFrames CLI (npx)."""
import json, sys, os, glob, shutil, subprocess
cards=json.load(open(sys.argv[1])); out=sys.argv[2]; os.makedirs(out,exist_ok=True)
W,H=1080,1350
proj='/home/claude/hf/cards'
if os.path.exists(proj): shutil.rmtree(proj)
shutil.copytree(os.path.dirname(os.path.abspath(__file__))+'/skeleton',proj)
os.makedirs(proj+'/compositions')
clips=''
for i,c in enumerate(cards):
    n=len(c['big']); fs=min(300,int(800/(n*0.68))) if n<=9 else 110
    col=c.get('color','#FFFFFF')
    clips+=f'''<div id="c{i}" class="clip card" data-start="{i}" data-duration="1" data-track-index="{i}">
  <div class="brand">Agent Report</div>
  <div class="kick">{c['kicker']}</div>
  <div class="big" style="font-size:{fs}px;color:{col}">{c['big']}</div>
  <div class="sub">{c['sub']}</div>
  <div class="src">{c.get('source','')}</div>
</div>
'''
html=f'''<!doctype html><html><head><meta charset="UTF-8"><meta name="viewport" content="width={W}, height={H}">
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<style>*{{margin:0;padding:0;box-sizing:border-box}}html,body{{width:{W}px;height:{H}px;overflow:hidden;background:#05162D}}
.card{{position:absolute;inset:0;background:linear-gradient(160deg,#05162D 0%,#0A2A5C 60%,#05162D 100%);font-family:'Poppins',sans-serif;color:#fff}}
.card::before{{content:"";position:absolute;left:-200px;top:250px;width:900px;height:900px;border-radius:50%;background:radial-gradient(circle,rgba(27,129,253,.45),rgba(27,129,253,0) 65%)}}
.brand{{position:absolute;left:90px;top:90px;font-size:36px;font-weight:700;letter-spacing:1px}}
.kick{{position:absolute;left:90px;width:900px;top:300px;text-align:center;font-size:52px;font-weight:600;color:#8EC5FF}}
.big{{position:absolute;left:90px;width:900px;top:400px;height:400px;text-align:center;font-weight:900;line-height:1.1;white-space:nowrap;display:flex;align-items:center;justify-content:center}}
.sub{{position:absolute;left:140px;width:800px;top:840px;text-align:center;font-size:48px;font-weight:700;line-height:1.2}}
.src{{position:absolute;left:90px;width:900px;top:1200px;text-align:center;font-size:30px;font-weight:500;color:rgba(220,231,255,.75)}}
</style></head><body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{len(cards)}" data-width="{W}" data-height="{H}">
{clips}</div>
<script>window.__timelines=window.__timelines||{{}};window.__timelines["main"]=gsap.timeline({{paused:true}});</script>
</body></html>'''
open(proj+'/index.html','w').write(html)
ts=','.join(str(i+0.5) for i in range(len(cards)))
subprocess.run(['npx','--yes','hyperframes@0.9.81','snapshot','--at',ts],cwd=proj,check=True)
snap=sorted(glob.glob(proj+'/.hyperframes/artifacts/snapshots/*/'),key=os.path.getmtime)[-1]
files=sorted(glob.glob(snap+'frame-*.png'))
assert len(files)>=len(cards),(len(files),len(cards))
files=files[:len(cards)]
for c,f in zip(cards,files): shutil.copy(f,f"{out}/{c['id']}.png")
print('wrote',len(files),'cards to',out)
