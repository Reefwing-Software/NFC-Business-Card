"""Use the supplied C0603 footprint for the DNP tuning capacitor."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def apply(pcb,uid):
 src=json.load(open(ROOT/'libraries/C14663-footprint.json'));ox=float(src['head']['x']);oy=float(src['head']['y'])
 for index,shape in enumerate(pcb['shape']):
  if not shape.startswith('LIB~'):continue
  q=shape.split('#@$')
  if not any(b.startswith('TEXT~P~') and b.split('~')[10]=='C1' for b in q):continue
  h=q[0].split('~');cx,cy=float(h[1]),float(h[2]);h[4]='180';h[8]=src['head']['uuid'];h[3]='package`C0603`nameAlias`Value`Value`DNP / C0G tuning`';h[12]='no'
  def px(x):return f'{cx+ox-float(x):.6f}'
  def py(y):return f'{cy+oy-float(y):.6f}'
  def points(s):return ' '.join((px if i%2==0 else py)(v) for i,v in enumerate(re.findall(r'-?\d+(?:\.\d+)?',s)))
  def path(s):
   def sub(m):
    c=m[1];v=re.findall(r'-?\d+(?:\.\d+)?',m[2]);w=[]
    for i,n in enumerate(v):
     if c in 'MLCQST':w.append((px if i%2==0 else py)(n))
     elif c=='A':w.append(px(n) if i%7==5 else py(n) if i%7==6 else n)
     elif c in 'mlcqsthv':w.append(f'{-float(n):g}')
     elif c=='H':w.append(px(n))
     elif c=='V':w.append(py(n))
     else:w.append(n)
    return c+' '+' '.join(w)+' '
   return re.sub(r'([MLCQSTAHVZmlcqstahvz])([^MLCQSTAHVZmlcqstahvz]*)',sub,s)
  body=[]
  for a in src['shape']:
   t=a.split('~');k=t[0]
   if k=='SVGNODE':continue # Library 3D-model transform, not fabrication geometry.
   if k=='PAD':
    t[2]=px(t[2]);t[3]=py(t[3]);t[10]=points(t[10]);t[11]=str((float(t[11])+180)%360);t[7]='ANT_A' if t[8]=='1' else 'ANT_B';t[17]='-393.70079'
    if len(t)>19 and t[19]:t[19]=','.join(points(t[19]).split())
   elif k=='TRACK':t[4]=points(t[4])
   elif k=='SOLIDREGION':t[3]=path(t[3])
   elif k=='ARC':t[4]=path(t[4])
   elif k=='CIRCLE':t[1]=px(t[1]);t[2]=py(t[2])
   else:raise ValueError(k)
   body.append(re.sub(r'(?<=~)gge[A-Za-z0-9_]+(?=~|$)',lambda m:uid(),'~'.join(t)))
  pcb['shape'][index]='#@$'.join(['~'.join(h)]+[b for b in q if b.startswith('TEXT~')]+body)
  return
 raise ValueError('Missing C1')
