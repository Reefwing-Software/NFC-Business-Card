import json,math,itertools
from pathlib import Path
from PIL import Image,ImageDraw,ImageFont
P=Path(__file__).parent;ROOT=P.parents[1];p=json.load(open(ROOT/'Reefwing-PCB-RevD.json'));BX=4047.559;BY=3046.343
(P/'validation.json').unlink(missing_ok=True)
objects=[];labels=[]
def pt(x,y):return((float(x)-BX)*.254,(float(y)-BY)*.254)
def add(kind,geom,r,net,layer,ref):objects.append({'kind':kind,'g':geom,'r':r,'net':net,'layer':layer,'ref':ref})
def parse(s,ref=''):
 t=s.split('~');k=t[0]
 if k=='LIB':
  q=s.split('#@$');ref=next(a.split('~')[10] for a in q if a.startswith('TEXT~P~'));labels.append((ref,pt(t[1],t[2])))
  for a in q[1:]:parse(a,ref)
 elif k=='TRACK' and t[2] in ['1','2']:
  v=list(map(float,t[4].split()));vv=[pt(*a) for a in zip(v[::2],v[1::2])]
  for a,b in zip(vv,vv[1:]):add('seg',[a,b],float(t[1])*.254/2,t[3] or 'COIL',int(t[2]),ref or t[5])
 elif k=='PAD':
  net=t[7] or 'NC_'+ref+t[8];c=pt(t[2],t[3]);r=float(t[4])*.254/2
  if t[1]=='ELLIPSE':add('seg',[c,c],r,net,int(t[6]),ref+'.'+t[8])
  else:
   v=list(map(float,t[10].split()));vv=[pt(*a) for a in zip(v[::2],v[1::2])];add('poly',vv,0,net,int(t[6]),ref+'.'+t[8])
 elif k=='VIA':
  c=pt(t[1],t[2]);
  for layer in [1,2]:add('seg',[c,c],float(t[3])*.254/2,t[4],layer,t[6])
for s in p['shape']:parse(s)
def pointseg(p,a,b):
 dx=b[0]-a[0];dy=b[1]-a[1];d=dx*dx+dy*dy
 t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d)) if d else 0
 return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)
def cross(a,b,c):return(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def segdist(a,b,c,d):
 if max(min(a[0],b[0]),min(c[0],d[0]))<=min(max(a[0],b[0]),max(c[0],d[0]))+1e-9 and max(min(a[1],b[1]),min(c[1],d[1]))<=min(max(a[1],b[1]),max(c[1],d[1]))+1e-9 and cross(a,b,c)*cross(a,b,d)<=0 and cross(c,d,a)*cross(c,d,b)<=0:return 0
 return min(pointseg(a,c,d),pointseg(b,c,d),pointseg(c,a,b),pointseg(d,a,b))
def inside(pt,poly):
 x,y=pt;v=False
 for a,b in zip(poly,poly[1:]+poly[:1]):
  if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:v=not v
 return v
for o in objects:
 g=o['g'];o['box']=(min(a[0] for a in g)-o['r'],min(a[1] for a in g)-o['r'],max(a[0] for a in g)+o['r'],max(a[1] for a in g)+o['r']);o['edges']=[g] if o['kind']=='seg' else list(zip(g,g[1:]+g[:1]))
errors=[];intentional=0
for a,b in itertools.combinations(objects,2):
 if a['layer']!=b['layer'] or a['net']==b['net']:continue
 A=a['box'];B=b['box']
 if A[0]>B[2]+.15 or B[0]>A[2]+.15 or A[1]>B[3]+.15 or B[1]>A[3]+.15:continue
 dd=min(segdist(*e,*f) for e in a['edges'] for f in b['edges'])
 if a['kind']=='poly' and any(inside(q,a['g']) for q in b['g']) or b['kind']=='poly' and any(inside(q,b['g']) for q in a['g']):dd=0
 dd-=a['r']+b['r']
 if dd<.149 and 'COIL' in [a['net'],b['net']] and any(n in ['ANT_A','ANT_B'] for n in [a['net'],b['net']]):
  other=b if a['net']=='COIL' else a
  terminal=next(o for o in objects if o['ref']==('L1.1' if other['net']=='ANT_A' else 'L1.2'))['g'][0]
  assert min(pointseg(terminal,*e) for e in other['edges'])<.31, 'Unexpected RF net overlap'
  intentional+=1;continue
 if dd<.149:errors.append({'a':a['ref'],'b':b['ref'],'nets':[a['net'],b['net']],'clearance_mm':round(dd,4),'location':a['g'][0]})
(P/'pcb-clearance-report.json').write_text(json.dumps({'minimum_required_mm':.15,'violations':errors,'intentional_RF_pairs_excluded':intentional,'limitations':['RF winding connections reviewed separately','This report covers copper clearance only; see validation.json for pad-mask/silk and board-edge checks']},indent=2)+'\n')
print('Clearance violations:',len(errors));print(json.dumps(errors[:15],indent=2))
# Independent connectivity: union touching copper shapes, including plated vias.
via_ids={s.split('~')[6] for s in p['shape'] if s.startswith('VIA~')}
parent=list(range(len(objects)))
def root(i):
 while parent[i]!=i:parent[i]=parent[parent[i]];i=parent[i]
 return i
def join(i,j):parent[root(i)]=root(j)
for i,a in enumerate(objects):
 for j in range(i):
  b=objects[j]
  if a['net']!=b['net']:continue
  if a['layer']!=b['layer']:
   if a['ref']==b['ref'] and a['ref'] in via_ids:join(i,j)
   continue
  A=a['box'];B=b['box']
  if A[0]>B[2]+1e-4 or B[0]>A[2]+1e-4 or A[1]>B[3]+1e-4 or B[1]>A[3]+1e-4:continue
  dd=min(segdist(*e,*f) for e in a['edges'] for f in b['edges'])
  if a['kind']=='poly' and any(inside(q,a['g']) for q in b['g']) or b['kind']=='poly' and any(inside(q,b['g']) for q in a['g']):dd=0
  if dd<=a['r']+b['r']+1e-4:join(i,j)
netpads={}
for i,a in enumerate(objects):
 if '.' in a['ref'] and not a['net'].startswith('NC_'):netpads.setdefault(a['net'],[]).append(i)
unconnected={n:[objects[i]['ref'] for i in ii] for n,ii in netpads.items() if len({root(i) for i in ii})>1}
(P/'pcb-connectivity-report.json').write_text(json.dumps({'status':'PASS' if not unconnected else 'FAIL','nets_checked':len(netpads),'unconnected':unconnected,'note':'Antenna modeled as two separate RF nets; winding continuity is intentional.'},indent=2)+'\n')
print('Connectivity:',len(netpads),'nets;',len(unconnected),'unconnected groups')
assert not errors, 'Copper clearance failure'
assert not unconnected, 'Disconnected copper'

# Independent schematic-to-PCB check with manufacturer pin roles (not Rev C
# symbol assumptions). Test labels and all physical pads must match.
sch=json.load(open(ROOT/'Reefwing-NFC-Card-RevD.json'))['schematics'][0]['dataStr']['shape']
parents={}
def find(a):
 parents.setdefault(a,a)
 if parents[a]!=a:parents[a]=find(parents[a])
 return parents[a]
def union(a,b):parents[find(a)]=find(b)
def point(x,y):return (float(x),float(y))
pins={};names=[];nc=set();roles={};components={}
for a in sch:
 t=a.split('~')
 if t[0]=='W':
  v=list(map(float,t[1].split()));ps=list(zip(v[::2],v[1::2]))
  for a,b in zip(ps,ps[1:]):union(a,b)
 elif t[0]=='N':names.append((point(t[1],t[2]),t[5]))
 elif t[0]=='O':nc.add(point(t[1],t[2]))
 elif t[0]=='LIB':
  q=a.split('#@$');r=next(b.split('~')[12] for b in q if b.startswith('T~P~'))
  assert r not in components,r
  components[r]=q
  for b in q:
   if b.startswith('P~'):
    z=b.split('^^');v=z[0].split('~');key=r+'.'+v[3]
    pins[key]=point(v[4],v[5]);roles[key]=z[3].split('~')[4]
for pos,name in names:union(pos,('NET',name))
snets={}
for key,pos in pins.items():
 ns={n for a,n in names if find(a)==find(pos)}
 assert len(ns)<=1,(key,ns)
 snets[key]=next(iter(ns)) if ns else 'NC' if pos in nc else 'UNLABELLED'
pads={};footprints={}
for a in p['shape']:
 if a.startswith('LIB~'):
  q=a.split('#@$');r=next(b.split('~')[10] for b in q if b.startswith('TEXT~P~'));footprints[r]=q
  for b in q:
   if b.startswith('PAD~'):
    z=b.split('~');pads[r+'.'+z[8]]=z
assert len(components)==len(footprints)==31
assert set(pins)==set(pads)
for k,v in pads.items():assert snets[k]==(v[7] or 'NC'),(k,snets[k],v[7])
expected={'U1.1':'ANT_A','U1.2':'GND','U1.3':'SCL','U1.4':'FD_N','U1.5':'SDA','U1.6':'VDD','U1.7':'VH','U1.8':'ANT_B',
'U2.1':'SCL','U2.2':'FD_N','U2.3':'GND','U2.4':'VDD','U2.19':'UPDI','U2.20':'SDA','U2.21':'GND',
'J1.1':'GND','J1.2':'VDD','J1.3':'UPDI','JP1.1':'VH','JP1.2':'VDD','C2.1':'VH','C2.2':'GND','C3.1':'VDD','C3.2':'GND',
'R10.1':'VDD','R10.2':'SCL','R11.1':'VDD','R11.2':'SDA','R12.1':'VDD','R12.2':'FD_N','C1.1':'ANT_A','C1.2':'ANT_B','L1.1':'ANT_A','L1.2':'ANT_B'}
for i,(pin,name) in enumerate(zip([5,6,7,8,14,13,12,11,10],['IN1','IN2','IN3','H1','H2','H3','H4','OUT1','OUT2']),1):
 expected.update({f'U2.{pin}':'LED_'+name,f'R{i}.1':'LED_'+name,f'R{i}.2':f'R{i}_2',f'D{i}.1':f'R{i}_2',f'D{i}.2':'GND'})
 assert roles[f'D{i}.1']=='A' and roles[f'D{i}.2']=='K'
 assert float(pads[f'D{i}.1'][2])<float(pads[f'D{i}.2'][2]),'Anode must face resistor'
 assert float(footprints[f'D{i}'][0].split('~')[4])==180
for pin in [9,15,16,17,18]:expected[f'U2.{pin}']='NC'
for k,n in expected.items():assert snets[k]==n,(k,n,snets[k])
assert pads['J1.1'][1]=='RECT'
for r in ['C1','L1','J1','JP1']+[f'TP{i}' for i in range(1,3)]:assert footprints[r][0].split('~')[12]=='no',r
for i in range(1,3):
 z=pads[f'TP{i}.1'];assert abs(float(z[4])*.254-1.5)<1e-5 and float(z[17])<0 and float(z[18])>0
# Rev C sources must remain untouched.
import hashlib
for f,h in json.load(open(P/'source-hashes.json')).items():assert hashlib.sha256((ROOT/f).read_bytes()).hexdigest()==h
# RF geometry is unchanged; intentional winding joins need native DRC review.
old=json.load(open(ROOT/'Reefwing-PCB-RevC.json'))
old_l1=next(a for a in old['shape'] if a.startswith('LIB~') and '#@$TEXT~P~' in a and any(b.startswith('TEXT~P~') and b.split('~')[10]=='L1' for b in a.split('#@$')))
assert [b for b in old_l1.split('#@$') if b.startswith(('TRACK~','PAD~'))]==[b for b in footprints['L1'] if b.startswith(('TRACK~','PAD~'))]
report={'status':'PASS','components':len(components),'pins':len(pins),'connected_nets':len(netpads),'schematic_pin_nets':snets,'led_pin_roles':{'1':'A','2':'K'},'led_rotation_deg':180,'test_pads':2,'limitations':['Independent geometry and netlist checks, not native EasyEDA ERC/DRC or Gerber validation.','Intentional antenna winding contacts excluded from inter-net clearance check; RF geometry unchanged.','Physical assembly orientation still requires JLCPCB preview and first-article verification.']}

print('PASS: schematic/PCB pin nets, manufacturer LED roles, rotations, exclusions and source preservation')

# Board contour, edge clearance, and silk-to-exposed-pad checks.
import sys,re
from shapely.geometry import Polygon,LineString,Point,box
from shapely.ops import unary_union
board=box(3,3,82,52).buffer(3,resolution=128)
def geometry(o):
 return Polygon(o['g']) if o['kind']=='poly' else LineString(o['g']).buffer(o['r'],resolution=32)
geoms=[geometry(o) for o in objects]
assert all(board.contains(g) for g in geoms)
edge=min(g.distance(board.boundary) for g in geoms);assert edge>.3
outline=[a.split('~') for a in p['shape'] if a.startswith(('TRACK~','ARC~')) and a.split('~')[2]=='10']
assert len(outline)==8 and sum(a[0]=='ARC' for a in outline)==4
ends=[]
for t in outline:
 if t[0]=='TRACK':
  v=list(map(float,t[4].split()));ends.extend([tuple(v[:2]),tuple(v[-2:])])
 else:
  v=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',t[4])));assert abs(v[2]*.254-3)<1e-5 and v[2]==v[3]
  ends.extend([tuple(v[:2]),tuple(v[-2:])])
assert all(sum(math.dist(a,b)<1e-5 for b in ends)==2 for a in ends)
mask=unary_union([geometry(o).buffer(.075+.15-1e-4) for o in objects if o['layer']==1 and '.' in o['ref']])
silkerrors=[]
for a in p['shape']:
 for b in (a.split('#@$')[1:] if a.startswith('LIB~') else [a]):
  t=b.split('~');g=None
  if t[0]=='SOLIDREGION' and t[1]=='3':
   v=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',t[3])));g=Polygon([pt(*z) for z in zip(v[::2],v[1::2])])
  elif t[0]=='TRACK' and t[2]=='3':
   v=list(map(float,t[4].split()));g=LineString([pt(*z) for z in zip(v[::2],v[1::2])]).buffer(float(t[1])*.254/2)
  if g is not None and g.intersection(mask).area>1e-6:silkerrors.append({'id':t[-1],'area':g.intersection(mask).area,'bounds':g.bounds})
if silkerrors:print('Silk examples:',silkerrors[:5])
assert not silkerrors,len(silkerrors)
report.update(board_size_mm=[85,55],corner_radius_mm=3,minimum_copper_to_edge_mm=round(edge,3),silk_to_pad_mask_clearance_mm=.15,intentional_RF_contacts= intentional)

print('PASS: closed rounded outline, copper/edge clearance, silkscreen pad relief; edge minimum',round(edge,3),'mm')

# Physical package placement checked against datasheet top-view pin order.
# U1 uses the datasheet orientation; the U2 supplier footprint is rotated
# relative to its datasheet drawing, as documented in README.md.
u1={1:(10.4,32.5),2:(10.4,33),3:(10.4,33.5),4:(11,33.6),5:(11.6,33.5),6:(11.6,33),7:(11.6,32.5),8:(11,32.4)}
u2={1:(20.2,41.5),2:(20.6,41.5),3:(21,41.5),4:(21.4,41.5),5:(21.8,41.5),6:(22.5,40.8),7:(22.5,40.4),8:(22.5,40),9:(22.5,39.6),10:(22.5,39.2),11:(21.8,38.5),12:(21.4,38.5),13:(21,38.5),14:(20.6,38.5),15:(20.2,38.5),16:(19.5,39.2),17:(19.5,39.6),18:(19.5,40),19:(19.5,40.4),20:(19.5,40.8),21:(21,40)}
for ref,positions in [('U1',u1),('U2',u2)]:
 for pin,position in positions.items():
  z=pads[f'{ref}.{pin}'];assert math.dist(pt(z[2],z[3]),position)<.005,(ref,pin)
assert all(float(pads[f'C1.{i}'][17])<0 for i in [1,2])
report['ic_land_orientation']='PASS: XQFN8 and VQFN20 top-view pin positions checked'

print('PASS: U1/U2 physical pin order and C1 paste exclusion')

assert {k for k in pads if k.startswith('TP')}=={'TP1.1','TP2.1'}
assert snets['TP1.1']=='GND' and snets['TP2.1']=='VDD'
for k in ['TP1.1','TP2.1']:
 z=pads[k];assert pt(z[2],z[3])[0]+.75<=24.0, 'Test pad must remain left of programming connector'
print('PASS: exactly two supply test pads, both left of J1')
report['supply_test_pad_placement']='PASS: exactly TP1 GND and TP2 VDD, both entirely left of x=24 mm; J1 starts at x=24.71 mm'
(P/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
