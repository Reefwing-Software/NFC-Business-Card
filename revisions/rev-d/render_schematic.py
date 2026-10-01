"""Review preview of the actual native schematic primitives and net labels."""
import json,html
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
s=json.load(open(R/'Reefwing-NFC-Card-RevD.json'))['schematics'][0]['dataStr']['shape']
out=['<svg xmlns="http://www.w3.org/2000/svg" width="2400" height="1860" viewBox="0 0 1600 1240"><rect width="1600" height="1240" fill="white"/>']
def text(x,y,value,size=9,color='#17324d',anchor='start'):
 out.append(f'<text x="{x}" y="{y}" font-family="Arial,sans-serif" font-size="{size}" fill="{color}" text-anchor="{anchor}">{html.escape(value)}</text>')
def path(d,color,width=1,fill='none'):out.append(f'<path d="{d}" stroke="{color}" stroke-width="{width}" fill="{fill}"/>')
def draw(a):
 t=a.split('~');k=t[0]
 if k=='LIB':
  for b in a.split('#@$')[1:]:draw(b)
 elif k=='T' and t[13]=='1':text(t[2],t[3],t[12],float(t[7].replace('pt','') or 9),t[5],t[14])
 elif k=='T':pass
 elif k=='R':out.append(f'<rect x="{t[1]}" y="{t[2]}" width="{t[5]}" height="{t[6]}" fill="{t[10]}" stroke="{t[7]}" stroke-width="{t[8]}"/>')
 elif k=='E':out.append(f'<ellipse cx="{t[1]}" cy="{t[2]}" rx="{t[3]}" ry="{t[4]}" fill="{t[8]}" stroke="{t[5]}" stroke-width="{t[6]}"/>')
 elif k=='PL':out.append(f'<polyline points="{t[1]}" fill="{t[5]}" stroke="{t[2]}" stroke-width="{t[3]}"/>')
 elif k=='PT':path(t[1],t[2],t[3],t[5])
 elif k=='P':
  z=a.split('^^');v=z[2].split('~');path(v[0],v[1])
  for j in [3,4]:
   v=z[j].split('~')
   if v[0]=='1':text(v[1],v[2],v[4],7,'#17324d',v[5])
 elif k=='N':text(t[8],t[9],t[5],6,t[4],t[7])
 elif k=='O':path(t[4],t[5])
 elif k=='W':out.append(f'<polyline points="{t[1]}" fill="none" stroke="#008000"/>')
 else:raise ValueError(k)
for a in s:draw(a)
out.append('</svg>');(P/'schematic.svg').write_text(''.join(out))
