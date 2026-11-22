import json, sys, os, shutil, subprocess
HERE=os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
rid=sys.argv[1]
spec=json.load(open(f'specs/{rid}.json'))
subprocess.run(['python3','gen_audio.py',f'specs/{rid}.json'],check=True,cwd=HERE)
d=json.load(open(f'video/public/{rid}.json'))
L=d['lines']; W,H=1080,1920
DUR=round(d['duration']+0.5,2)
proj=f'/home/claude/hf/{rid}'
os.makedirs('/home/claude/hf',exist_ok=True)
if os.path.exists(proj): shutil.rmtree(proj)
shutil.copytree(HERE+'/skeleton',proj,ignore=shutil.ignore_patterns('gen.py','index.html','compositions','assets','.hyperframes','check.json','node_modules'))
os.makedirs(proj+'/compositions'); os.makedirs(proj+'/assets')
shutil.copy(f'video/public/{rid}.wav',proj+'/assets/voice.wav')
def tpl(sid,body,script,style=''):
    return f'''<template>
  <style>
    #root {{ position:absolute; inset:0; font-family:'Poppins',sans-serif; color:#fff; }}
    #root .abs {{ position:absolute; }}
    {style}
  </style>
  <div id="root" data-composition-id="{sid}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{script}
    window.__timelines["{sid}"] = tl;
  </script>
</template>
'''
scenes=[]
for i,l in enumerate(L):
    st=l['start'] if i>0 else 0.0
    nx=L[i+1]['start'] if i+1<len(L) else DUR
    du=round(nx-st,2)
    sid=f's{i+1}'
    col=l.get('color','#FFFFFF')
    t=l['type']
    if t=='big':
        n=len(l['big']); fs=min(260,int(768/(n*0.68)))
        body=f'''    <div id="{sid}-k" class="abs" style="left:120px;width:768px;top:430px;text-align:center;font-size:46px;font-weight:600;color:#8EC5FF">{l['kicker']}</div>
    <div id="{sid}-n" class="abs" style="left:120px;width:768px;top:560px;height:290px;text-align:center;font-size:{fs}px;font-weight:900;line-height:1.05;white-space:nowrap;color:{col}">{l['big']}</div>
    <div id="{sid}-s" class="abs" style="left:170px;width:640px;top:880px;text-align:center;font-size:44px;font-weight:700;line-height:1.2">{l['sub']}</div>'''
        js=f'''    tl.fromTo("#{sid}-k",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.35,ease:"power3.out"}},0.05);
    tl.fromTo("#{sid}-n",{{opacity:0,scale:0.7}},{{opacity:1,scale:1,duration:0.45,ease:"back.out(1.6)"}},0.15);
    tl.fromTo("#{sid}-s",{{opacity:0,y:30}},{{opacity:1,y:0,duration:0.4,ease:"power3.out"}},0.6);'''
    elif t=='text':
        body=f'''    <div id="{sid}-t" class="abs" style="left:120px;width:768px;top:470px;text-align:center;font-size:88px;font-weight:900;line-height:1.15">{l['text']}</div>
    <div id="{sid}-s" class="abs" style="left:170px;width:640px;top:800px;text-align:center;font-size:36px;font-weight:600;color:#8EC5FF">{l['sub']}</div>'''
        js=f'''    tl.fromTo("#{sid}-t",{{opacity:0,scale:0.9}},{{opacity:1,scale:1,duration:0.5,ease:"power3.out"}},0.1);
    tl.fromTo("#{sid}-s",{{opacity:0}},{{opacity:1,duration:0.4}},0.8);'''
    elif t=='bars':
        mx=max(r[1] for r in l['rows']); BM=300
        bars=''; js=f'    tl.fromTo("#{sid}-h",{{opacity:0}},{{opacity:1,duration:0.3}},0.05);\n'
        words=l['words']
        for j,(nm,v,dsp,wi) in enumerate(l['rows']):
            y=510+j*120; w=max(8,int(v/mx*BM))
            bars+=f'<div id="{sid}-l{j}" class="abs" style="left:120px;top:{y}px;font-size:38px;font-weight:700;width:210px">{nm}</div><div id="{sid}-b{j}" class="abs" style="left:350px;top:{y+4}px;height:66px;width:{w}px;background:#FF5C5C;border-radius:14px;transform-origin:left center"></div><div id="{sid}-v{j}" class="abs" style="left:{350+w+18}px;top:{y}px;font-size:46px;font-weight:900;white-space:nowrap">{dsp}</div>'
            lt=max(0.1,words[wi]['s']-l['start'])
            js+=f'''    tl.fromTo("#{sid}-l{j}",{{opacity:0,x:-40}},{{opacity:1,x:0,duration:0.3}},{lt:.2f});
    tl.fromTo("#{sid}-b{j}",{{scaleX:0}},{{scaleX:1,duration:0.6,ease:"power3.out"}},{lt+0.1:.2f});
    tl.fromTo("#{sid}-v{j}",{{opacity:0}},{{opacity:1,duration:0.3}},{lt+0.5:.2f});
'''
        body=f'''    <div id="{sid}-h" class="abs" style="left:120px;width:768px;top:395px;text-align:center;font-size:40px;font-weight:600;color:#8EC5FF">{l['title']}</div>
    {bars}'''
    else:
        body=f'''    <div id="{sid}-a" class="abs" style="left:120px;width:768px;top:500px;text-align:center;font-size:96px;font-weight:900;line-height:1.1">Agent Report</div>
    <div id="{sid}-b" class="abs" style="left:120px;width:768px;top:700px;text-align:center;font-size:48px;font-weight:600;color:#8EC5FF;line-height:1.2">Follow for the AI news that matters</div>'''
        js=f'''    tl.fromTo("#{sid}-a",{{opacity:0,scale:0.85}},{{opacity:1,scale:1,duration:0.4,ease:"back.out(1.5)"}},0.1);
    tl.fromTo("#{sid}-b",{{opacity:0,y:20}},{{opacity:1,y:0,duration:0.4}},0.45);'''
    scenes.append((sid,st,du,tpl(sid,body,js)))
for sid,st,du,html in scenes: open(f'{proj}/compositions/{sid}.html','w').write(html)
groups=[]
for l in L:
    ws=l['words']
    for i in range(0,len(ws),4): groups.append(ws[i:i+4])
gh='';gj=''
for gi,g in enumerate(groups):
    s=max(0.12,g[0]['s']-0.05); e=g[-1]['e']+0.1
    nxt=groups[gi+1][0]['s']-0.05 if gi+1<len(groups) else DUR
    e=min(e,nxt-0.02)
    words=' '.join(f'<span id="cw{gi}_{k}" class="w">{w["w"]}</span>' for k,w in enumerate(g))
    gh+=f'    <div id="cg{gi}" class="clip grp" data-start="{s:.2f}" data-duration="{e-s:.2f}" data-track-index="0">{words}</div>\n'
    gj+=f'    tl.fromTo("#cg{gi}",{{opacity:0,y:16}},{{opacity:1,y:0,duration:0.12,ease:"power2.out"}},{s:.2f});\n'
    for k,w in enumerate(g):
        gj+=f'    tl.fromTo("#cw{gi}_{k}",{{color:"#B9C8E6",scale:1}},{{color:"#ffffff",scale:1.08,duration:0.08}},{w["s"]:.2f});\n'
        gj+=f'    tl.to("#cw{gi}_{k}",{{scale:1,duration:0.1}},{w["e"]:.2f});\n'
    gj+=f'    tl.to("#cg{gi}",{{opacity:0,duration:0.1,ease:"power2.in"}},{e-0.1:.2f});\n'
cap=f'''<template>
  <style>
    #root {{ position:absolute; inset:0; font-family:'Poppins',sans-serif; }}
    .grp {{ position:absolute; left:150px; width:708px; top:1070px; text-align:center; font-size:64px; font-weight:800; line-height:1.15; color:#fff; text-shadow:0 4px 18px rgba(0,0,0,0.55); overflow:visible; }}
    .w {{ display:inline-block; margin:0 9px; color:#B9C8E6; }}
  </style>
  <div id="root" data-composition-id="captions" data-width="{W}" data-height="{H}">
{gh}  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{gj}    window.__timelines["captions"] = tl;
  </script>
</template>
'''
open(f'{proj}/compositions/captions.html','w').write(cap)
hosts=''.join(f'    <div id="{sid}" data-composition-id="{sid}" data-composition-src="compositions/{sid}.html" data-start="{st}" data-duration="{du:.2f}" data-track-index="1" data-track-kind="graphics" data-width="{W}" data-height="{H}"></div>\n' for sid,st,du,_ in scenes)
index=f'''<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width={W}, height={H}" />
    <script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
    <style>
      * {{ margin:0; padding:0; box-sizing:border-box; }}
      html, body {{ margin:0; width:{W}px; height:{H}px; overflow:hidden; background:#05162D; }}
      #bg {{ position:absolute; inset:0; background:linear-gradient(160deg,#05162D 0%,#0A2A5C 60%,#05162D 100%); }}
      #glow1 {{ position:absolute; left:-200px; top:300px; width:900px; height:900px; border-radius:50%; background:radial-gradient(circle,rgba(27,129,253,0.45),rgba(27,129,253,0) 65%); }}
      #glow2 {{ position:absolute; left:500px; top:1000px; width:800px; height:800px; border-radius:50%; background:radial-gradient(circle,rgba(27,129,253,0.3),rgba(27,129,253,0) 65%); }}
      #brand {{ position:absolute; left:120px; top:306px; font-family:'Poppins',sans-serif; font-size:34px; font-weight:700; color:#fff; letter-spacing:1px; }}
      #prog {{ position:absolute; left:0; top:0; height:8px; width:100%; background:#1B81FD; transform-origin:left center; }}
    </style>
  </head>
  <body>
    <div id="root" data-composition-id="main" data-start="0" data-duration="{DUR}" data-width="{W}" data-height="{H}">
      <div id="bg"></div><div id="glow1"></div><div id="glow2"></div>
      <div id="prog"></div>
      <div id="brand">Agent Report</div>
{hosts}      <div id="capshost" data-composition-id="captions" data-composition-src="compositions/captions.html" data-start="0" data-duration="{DUR}" data-track-index="2" data-track-kind="captions" data-width="{W}" data-height="{H}"></div>
      <audio id="voice" src="assets/voice.wav" data-start="0" data-duration="{d['duration']}" data-track-index="3" data-volume="1"></audio>
    </div>
    <script>
      const tl = gsap.timeline({{ paused: true }});
      tl.fromTo("#glow1",{{x:0,y:0}},{{x:160,y:120,duration:{DUR},ease:"none"}},0);
      tl.fromTo("#glow2",{{x:0,y:0}},{{x:-180,y:-100,duration:{DUR},ease:"none"}},0);
      tl.fromTo("#prog",{{scaleX:0}},{{scaleX:1,duration:{DUR},ease:"none"}},0);
      window.__timelines["main"] = tl;
    </script>
  </body>
</html>
'''
open(f'{proj}/index.html','w').write(index)
print('built',proj,DUR)
