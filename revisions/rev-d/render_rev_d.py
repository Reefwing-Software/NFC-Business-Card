"""Render native PCB copper and silkscreen without altering artwork."""
import json,html
from pathlib import Path
P=Path(__file__).parent;R=P.parents[1];p=json.load(open(R/'Reefwing-PCB-RevD.json'))
BX=4047.559;BY=3046.343;U=.254
flat=[]
for a in p['shape']:flat.extend(a.split('#@$')[1:] if a.startswith('LIB~') else [a])
def render(layer,copper=False):
 out=[]
 for a in flat:
  t=a.split('~');k=t[0]
  col='#f5f3dd'
  if k=='TRACK' and int(t[2])==layer:out.append(f'<polyline points="{t[4]}" fill="none" stroke="{col}" stroke-width="{t[1]}" stroke-linejoin="round" stroke-linecap="round"/>')
  elif k=='SOLIDREGION' and int(t[1])==layer:out.append(f'<path d="{t[3]}" fill="{col}"/>')
  elif k=='TEXT' and int(t[7])==layer and t[11]:out.append(f'<path d="{t[11]}" fill="none" stroke="{col}" stroke-width="{t[4]}" stroke-linecap="round"/>')
  elif k=='CIRCLE' and int(t[5])==layer:out.append(f'<circle cx="{t[1]}" cy="{t[2]}" r="{t[3]}" fill="none" stroke="{col}" stroke-width="{t[4]}"/>')
 return ''.join(out)
def copper(layer,pads=True):
 out=[]
 for a in flat:
  t=a.split('~');k=t[0]
  if k=='TRACK' and int(t[2])==layer:out.append(f'<polyline points="{t[4]}" fill="none" stroke="#63886b" stroke-width="{t[1]}" stroke-linecap="round" stroke-linejoin="round"/>')
  elif k=='PAD' and int(t[6])==layer:
   if t[10]:out.append(f'<polygon points="{t[10]}" fill="#d6ad56"/>')
   else:out.append(f'<ellipse cx="{t[2]}" cy="{t[3]}" rx="{float(t[4])/2}" ry="{float(t[5])/2}" fill="#d6ad56"/>')
  elif k=='VIA':out.append(f'<circle cx="{t[1]}" cy="{t[2]}" r="{float(t[3])/2}" fill="#779071"/><circle cx="{t[1]}" cy="{t[2]}" r="{t[5]}" fill="#12352b"/>')
 return ''.join(out)
for side,layer in [('front',3),('back',4)]:
 mirror='translate(85 0) scale(-1 1)' if side=='back' else ''
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="1700" height="1100" viewBox="0 0 85 55"><rect width="85" height="55" rx="3" fill="#184839"/><g transform="{mirror}"><g transform="scale({U}) translate({-BX} {-BY})">'+copper(1 if side=='front' else 2)+render(layer)+'</g></g></svg>'
 (P/f'pcb-{side}.svg').write_text(s)
print('Native front/back SVG previews written')
