"""Place unmodified supplier symbols by translation, preserving pin roles.

Only instance IDs, reference/value text and placement coordinates are changed.
Footprint UUIDs come directly from the supplied symbol definitions.
"""
import json,re,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
CODES={'U1':'C710403','U2':'C2052778','C2':'C107100','C3':'C14663','R10':'C25804','R11':'C25804','R12':'C25803',**{f'D{i}':'C2286' for i in range(1,10)},**{f'R{i}':'C21190' for i in range(1,10)}}
def ref(q):return next(b.split('~')[12] for b in q if b.startswith('T~P~'))
def path(s,dx,dy):
 def move(m):
  c=m[1];v=[float(x) for x in re.findall(r'[-+]?(?:\d*\.\d+|\d+)',m[2])]
  if c in ['M','L','C','Q','S','T']:
   v=[n+(dy if i%2 else dx) for i,n in enumerate(v)]
  elif c=='H':v=[n+dx for n in v]
  elif c=='V':v=[n+dy for n in v]
  elif c=='A':v=[n+(dx if i%7==5 else dy if i%7==6 else 0) for i,n in enumerate(v)]
  return c+' '+' '.join(f'{n:g}' for n in v)+' '
 return re.sub(r'([MLCQSTAHVZmlcqstahvz])([^MLCQSTAHVZmlcqstahvz]*)',move,s)
def translate(b,dx,dy):
 t=b.split('~');k=t[0]
 def pair(i,j):t[i]=f'{float(t[i])+dx:g}';t[j]=f'{float(t[j])+dy:g}'
 if k=='P':
  z=b.split('^^');t=z[0].split('~');pair(4,5);z[0]='~'.join(t)
  for n in [1,3,4,5]:
   t=z[n].split('~');pair(0,1) if n==1 else pair(1,2);z[n]='~'.join(t)
  for n in [2,6]:
   t=z[n].split('~');j=0 if n==2 else 1;t[j]=path(t[j],dx,dy);z[n]='~'.join(t)
  return '^^'.join(z)
 if k in ['R','E']:pair(1,2)
 elif k=='T':pair(2,3)
 elif k=='PL':
  v=list(map(float,t[1].split()));t[1]=' '.join(f'{n+(dy if i%2 else dx):g}' for i,n in enumerate(v))
 elif k=='PT':t[1]=path(t[1],dx,dy)
 else:raise ValueError('Unsupported schematic primitive '+k)
 return '~'.join(t)
def apply(sch,pcb):
 old=sch['schematics'][0]['dataStr']['shape'];comps={ref(q):q for a in old if a.startswith('LIB~') for q in [a.split('#@$')]}
 nets={}
 for a in pcb['shape']:
  if not a.startswith('LIB~'):continue
  q=a.split('#@$');r=next(b.split('~')[10] for b in q if b.startswith('TEXT~P~'))
  for b in q:
   if b.startswith('PAD~'):
    t=b.split('~');nets[r+'.'+t[8]]=t[7] or 'NC'
 out=[];count=3100000
 def uid():
  nonlocal count
  count+=1;return 'gge'+str(count)
 def text(label,x,y,size=10):return f'T~L~{x}~{y}~0~#17324D~~{size}pt~~~~comment~{label}~1~start~{uid()}~0'
 out.extend([text('REEFWING / EMBEDDED AI - REV D',70,55,16),text('Supplied EasyEDA/LCSC symbols and linked footprints - 1 October 2026',70,80),text('NFC / POWER',70,120,12),text('ATtiny816 / PROGRAMMING',530,120,12),text('LED OUTPUTS - GPIO HIGH = ON',1100,120,12)])
 positions={'U1':(250,210),'U2':(750,230),'L1':(170,370),'C1':(390,370),'C2':(170,460),'C3':(390,460),'JP1':(250,550),'J1':(670,410),'R10':(590,630),'R11':(810,630),'R12':(590,740),'TP1':(150,690),'TP2':(350,690)}
 for i in range(1,10):positions[f'D{i}']=(1190,185+(i-1)*80);positions[f'R{i}']=(1420,185+(i-1)*80)
 manifest=[]
 for r,q in comps.items():
  x,y=positions[r];h=q[0].split('~')
  # C1 is DNP: use the standard capacitor graphics but no purchased SKU.
  code=CODES.get(r);sourcecode=code or ('C14663' if r=='C1' else None)
  if sourcecode:
   srcpath=ROOT/'libraries'/f'{sourcecode}-symbol.json';src=json.loads(srcpath.read_text());sh=src['head'];dx=x-float(sh['x']);dy=y-float(sh['y'])
   pa=dict(sh['c_para']);pa['nameAlias']='Value';value=pa.get('Value',pa.get('name',r))
   if r=='C1':
    value='DNP / C0G tuning';pa['name']='Optional C0G tuning capacitor'
    for key in ['Supplier','Supplier Part','Manufacturer','Manufacturer Part','JLCPCB Part Class']:pa.pop(key,None)
   pa['Value']=value;pa['pre']=re.sub(r'\d+$','?',r)
   h[3]='`'.join(z for kv in pa.items() for z in kv);h[7]=sh['puuid'];h[8]=sh['uuid'];h[4]='0'
   body=[translate(b,dx,dy) for b in src['shape']]
   # All source primitives and pin metadata are retained, with unique IDs.
   ids={m:uid() for b in body for m in re.findall(r'(?<=~)(?:gge|rep)[A-Za-z0-9_]+(?=~|$)',b)}
   body=[re.sub(r'(?<=~)(?:gge|rep)[A-Za-z0-9_]+(?=~|$)',lambda m:ids[m[0]],b) for b in body]
   top=min(float(b.split('^^')[0].split('~')[5]) for b in body if b.startswith('P~'))-30
   body=[f'T~P~{x}~{top}~0~#17324D~~9pt~~~~comment~{r}~1~middle~{uid()}~0',f'T~N~{x}~{top+13}~0~#17324D~~8pt~~~~comment~{value}~1~middle~{uid()}~0']+body
   manifest.append(dict(ref=r,code=sourcecode,populated=r!='C1',symbol_uuid=sh['uuid'],footprint_uuid=sh['puuid'],offset=[dx,dy],source_sha256=hashlib.sha256(srcpath.read_bytes()).hexdigest()))
  else:
   dx=x-float(h[1]);dy=y-float(h[2]);body=[translate(b,dx,dy) for b in q[1:]]
  h[1]=str(x);h[2]=str(y);h[6]=uid();out.append('#@$'.join(['~'.join(h)]+body))
  for b in body:
   if not b.startswith('P~'):continue
   t=b.split('^^')[0].split('~');px,py=float(t[4]),float(t[5]);net=nets[r+'.'+t[3]]
   if net=='NC':out.append(f'O~{px:g}~{py:g}~{uid()}~M {px-4:g} {py-4:g} L {px+4:g} {py+4:g} M {px-4:g} {py+4:g} L {px+4:g} {py-4:g}~#FF0000~0');continue
   left=float(t[6])==180;anchor='end' if left else 'start';tx=px-4 if left else px+4
   out.append(f'N~{px:g}~{py:g}~0~#0000FF~{net}~{uid()}~{anchor}~{tx:g}~{py-2:g}~~6pt~0')
 notes=['D1-D9: manufacturer pin 1 = A (+), pin 2 = K (-). Supplier symbol orientation retained.',
 'GPIO -> 1k resistor -> LED anode; cathode -> GND. PCB LED placement remains at 180 degrees.',
 'J1: GND / VDD / UPDI. Programming: JP1 OPEN, no NFC field, regulated 3.0 V with matching UPDI levels.',
 'Disconnect programmer before closing JP1 for NFC power. TP1 = GND; TP2 = VDD (3V).',
 'PA1=SDA, PA2=SCL: set PORTMUX.CTRLB |= PORTMUX_TWI0_bm before TWI initialization.',
 'FD_N: U1.4 -> U2.2 (PA3), 100k pull-up. Configure FD_ON=00 and FD_OFF=00 for field detection.',
 'Unused PB5 / PC0-PC3: pull-ups or disable digital inputs. Keep PA0 configured as UPDI.',
 '1 MHz internal clock for low current; prototype BOD disabled, verify fuses. No operation claimed below 1.8 V.',
 'C1 is DNP: tune antenna after measurement; do not short. C2+C3 = 182nF nominal; no bulk reservoir.',
 'URL provisioning: I2C sketch or RF. Avoid I2C activity during animation. Native ERC/DRC and assembly review pending.']
 out.extend(text(s,70,940+i*23,9) for i,s in enumerate(notes))
 sch['schematics'][0]['dataStr']['shape']=out
 sch['schematics'][0]['dataStr']['BBox']={'x':50,'y':20,'width':1500,'height':1180}
 sch['schematics'][0]['dataStr']['canvas']='CA~1600~1240~#FFFFFF~yes~#CCCCCC~5~1600~1240~line~5~pixel~5~0~0'
 (ROOT/'revisions/rev-d/supplier-symbols.json').write_text(json.dumps(manifest,indent=2)+'\n')
 return sch
if __name__=='__main__':
 p=ROOT/'Reefwing-NFC-Card-RevD.json';sch=json.loads(p.read_text());pcb=json.loads((ROOT/'Reefwing-PCB-RevD.json').read_text());apply(sch,pcb);p.write_text(json.dumps(sch,ensure_ascii=False,indent=2)+'\n')
