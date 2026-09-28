"""Build Rev D from immutable Rev C EasyEDA Standard files.

Requires numpy, matplotlib and shapely. Run from any directory. Does not
modify Rev C or publish/manufacture anything. Units in native files: 10 mil.
"""
import copy, json, math, re, sys, hashlib
from pathlib import Path
import numpy as np
from shapely.geometry import Point, LineString, Polygon, box
from shapely.ops import unary_union
from matplotlib.textpath import TextPath
from matplotlib.font_manager import FontProperties

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.append(str(ROOT/'artwork'))
from simple_polygons import split_contours
U=.254; BX=4047.559; BY=3046.343
counter=2000000
def uid():
    global counter
    counter+=1
    return 'gge'+str(counter)
def num(v): return f'{v:.6f}'
def xy(p): return (BX+p[0]/U, BY+p[1]/U)
def mm(x,y): return ((float(x)-BX)*U,(float(y)-BY)*U)
def points(v):
    n=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',v)))
    return list(zip(n[::2],n[1::2]))
def nativepts(ps):return ' '.join(num(v) for p in ps for v in xy(p))
def ref(q,sch=False):return next(b.split('~')[12 if sch else 10] for b in q if b.startswith('T~P~' if sch else 'TEXT~P~'))
def attrs(a):
    v=a.split('`');return dict(zip(v[::2],v[1::2]))
def encoded(d):return '`'.join(v for kv in d.items() for v in kv)
def pathpoly(path):return Polygon([mm(*p) for p in points(path)])
def solid(poly,layer=3):
    return f'SOLIDREGION~{layer}~~M '+ ' L '.join(' '.join(num(v) for v in xy(p)) for p in poly)+' Z~solid~'+uid()+'~~~~0'
font=FontProperties(family='DejaVu Sans',weight='bold')
def letters(label,x,y,h=.8):
    t=TextPath((0,0),label,size=100,prop=font); b=t.get_extents(); k=h/b.height
    cs=[[(x+(px-b.xmin)*k,y+(b.ymax-py)*k) for px,py in a] for a in t.to_polygons()]
    return [solid(a) for a in split_contours(cs)]

pcb=json.loads((ROOT/'Reefwing-PCB-RevC.json').read_text())
sch=json.loads((ROOT/'Reefwing-NFC-Card-RevC.json').read_text())
ss=sch['schematics'][0]['dataStr']['shape']
for node in [sch,sch['schematics'][0]]:
    node['title']='Reefwing NFC Card Rev D'
    node['description']='Rev D: corrected LED polarity, R3 mm board corners and diagnostic test pads.'
sch['schematics'][0]['dataStr']['head']['c_para']['name']='Reefwing Embedded AI NFC Card Rev D'
pcb['head']['c_para']['name']='Reefwing NFC Card Rev D'
for i,a in enumerate(ss):
    if a.startswith('LIB~'):
        q=a.split('#@$');r=ref(q,True)
        if re.fullmatch(r'D[1-9]',r):
            for j,b in enumerate(q):
                if b.startswith('P~'):
                    z=b.split('^^');t=z[0].split('~');new='1' if t[3]=='2' else '2';t[3]=new;z[0]='~'.join(t)
                    t=z[4].split('~');t[4]=new;z[4]='~'.join(t);q[j]='^^'.join(z)
            ss[i]='#@$'.join(q)
    else:
        ss[i]=a.replace('Rev C - review corrections | 2026-09-12','Rev D - LED polarity / test access | 2026-09-28').replace('1.25 MHz (20 MHz / 16)','1 MHz (16 MHz / 16)').replace('NFC URL is programmed over RF. I2C is available for configuration; avoid bus activity during animation.','Write the NFC URL using the I2C provisioning sketch or RF. Avoid I2C activity during animation.')

# Rotate each LED's complete supplier footprint 180 degrees. Reference text
# stays readable. Pin numbers keep manufacturer meaning: 1=A, 2=K.
def turn180(b,cx,cy):
    t=b.split('~');k=t[0]
    def pair(x,y):return num(2*cx-float(x)),num(2*cy-float(y))
    def ps(v):return ' '.join(w for x,y in points(v) for w in pair(x,y))
    def path(v):
        def subst(m):
            command=m[1];v=points(m[2]);return command+' '+' '.join(w for x,y in v for w in pair(x,y))+' '
        return re.sub(r'([ML])([^MLZ]+)',subst,v)
    if k=='PAD':
        t[2],t[3]=pair(t[2],t[3]);t[10]=ps(t[10]);t[11]=str((float(t[11])+180)%360)
        if len(t)>19 and t[19]:t[19]=','.join(ps(t[19]).split())
    elif k=='TRACK':t[4]=ps(t[4])
    elif k=='SOLIDREGION':t[3]=path(t[3])
    elif k=='CIRCLE':t[1],t[2]=pair(t[1],t[2])
    else:raise ValueError(k)
    return '~'.join(t)
for i,a in enumerate(pcb['shape']):
    if not a.startswith('LIB~'):continue
    q=a.split('#@$');r=ref(q);h=q[0].split('~')
    if r in ['C1','L1','J1','JP1']:h[12]='no'
    if r=='C1':
        for j,b in enumerate(q[1:],1):
            if b.startswith('PAD~'):
                t=b.split('~');t[17]='-393.70079';q[j]='~'.join(t)
    if re.fullmatch(r'D[1-9]',r):
        cx,cy=float(h[1]),float(h[2]);h[4]='180'
        for j,b in enumerate(q[1:],1):
            if b.startswith('TEXT~'):continue
            q[j]=turn180(b,cx,cy)
            if b.startswith('PAD~'):
                t=q[j].split('~');t[7]='R'+r[1:]+'_2' if t[8]=='1' else 'GND';q[j]='~'.join(t)
    q[0]='~'.join(h);pcb['shape'][i]='#@$'.join(q)

# Native connected lines and arcs, 85 x 55 mm, corner radius 3 mm.
pcb['shape']=[a for a in pcb['shape'] if not (a.startswith(('TRACK~','ARC~')) and a.split('~')[2]=='10')]
for a,b in [((3,0),(82,0)),((85,3),(85,52)),((82,55),(3,55)),((0,52),(0,3))]:
    pcb['shape'].append(f'TRACK~0.393701~10~~{nativepts([a,b])}~{uid()}~0')
for a,b in [((82,0),(85,3)),((85,52),(82,55)),((3,55),(0,52)),((0,3),(3,0))]:
    x,y=xy(a);xx,yy=xy(b)
    pcb['shape'].append(f'ARC~0.393701~10~~M {num(x)} {num(y)} A {num(3/U)} {num(3/U)} 0 0 1 {num(xx)} {num(yy)}~~{uid()}~0')
board=box(3,3,82,52).buffer(3,quad_segs=64)

def copper(p):
    result=[]
    def add(a,r=''):
        t=a.split('~');kind=t[0]
        if kind=='LIB':
            q=a.split('#@$');r=ref(q)
            for b in q[1:]:add(b,r)
        elif kind=='PAD':
            x,y=mm(t[2],t[3]);g=pathpoly(t[10]) if t[10] else Point(x,y).buffer(float(t[4])*U/2,quad_segs=24)
            result.append(dict(g=g,net=t[7] or 'NC_'+r+'.'+t[8],layer=int(t[6]),ref=r+'.'+t[8],pad=True,center=(x,y)))
        elif kind=='TRACK' and t[2] in ['1','2']:
            g=LineString([mm(*v) for v in points(t[4])]).buffer(float(t[1])*U/2,quad_segs=12)
            result.append(dict(g=g,net=t[3] or 'COIL',layer=int(t[2]),ref=r or t[5],pad=False))
        elif kind=='VIA':
            for layer in [1,2]:result.append(dict(g=Point(mm(t[1],t[2])).buffer(float(t[3])*U/2,quad_segs=24),net=t[4],layer=layer,ref=t[6],via=True,pad=False))
        elif kind=='SOLIDREGION' and t[1] in ['1','2']:
            result.append(dict(g=pathpoly(t[3]),net=t[2],layer=int(t[1]),ref=r or t[5],pad=False))
    for a in p['shape']:add(a)
    return result
objects=copper(pcb)
padmap={o['ref']:o for o in objects if o['pad']}
targets=[('GND','J1.1'),('VDD','J1.2'),('VH','C2.1'),('SDA','R11.2'),('SCL','R10.2'),('FD','R12.2'),('UPDI','J1.3')]
for i in range(1,10):targets.extend([(f'G{i}',f'R{i}.1'),(f'A{i}',f'R{i}.2')])
testpoints=[]
# Find a short, clear top-layer branch for each 1.5 mm exposed test pad.
# New pads cannot occupy existing component lands or bodies, even same-net.
bodies=[]
for a in pcb['shape']:
    if a.startswith('LIB~'):
        q=a.split('#@$');r=ref(q)
        if r in ['L1','J1']:continue
        gs=[o['g'] for o in objects if o['pad'] and o['ref'].split('.')[0]==r]
        if gs:bodies.append(unary_union(gs).envelope.buffer(.25))
bodyunion=unary_union(bodies)
for index,(label,anchor) in enumerate(targets,1):
    refname='TP'+str(index);source=padmap[anchor];net=source['net'];origin=source['center']
    obstacles=unary_union([o['g'] for o in objects if o['layer']==1 and o['net']!=net])
    padobstacles=unary_union([o['g'] for o in objects if o['pad']])
    candidates=[]
    for route_layer in [1,2]:
        route_obstacles=unary_union([o['g'] for o in objects if o['layer']==route_layer and o['net']!=net])
        origins=[origin] if route_layer==1 else []
        for trace in pcb['shape']:
            z=trace.split('~')
            if z[0]=='TRACK' and z[2]==str(route_layer) and z[3]==net:
                origins.extend(mm(*v) for v in points(z[4]) if Point(mm(*v)).distance(Point(origin))<12)
        origins=list(dict.fromkeys(origins))
        for radius in np.arange(1.7,10.01,.25):
            for angle in range(0,360,15):
                a=math.radians(angle);c=(round(origin[0]+radius*math.cos(a),3),round(origin[1]+radius*math.sin(a),3))
                disk=Point(c).buffer(.75,quad_segs=24)
                if not box(8.5,9,76.5,46).contains(disk):continue
                if disk.distance(obstacles)<.20 or disk.distance(bodyunion)<.35 or disk.distance(padobstacles)<.60:continue
                if route_layer==2 and Point(c).buffer(.3).distance(route_obstacles)<.15:continue
                for ps in [[o,c] for o in origins]+[[o,(o[0],c[1]),c] for o in origins]+[[o,(c[0],o[1]),c] for o in origins]:
                    branch=LineString(ps).buffer(.10,quad_segs=12)
                    if branch.distance(route_obstacles)<.15-1e-5:continue
                    score=LineString(ps).length + (0 if c[1]>origin[1]+1 else .4) + (4 if route_layer==2 else 0)
                    candidates.append((score,c,ps,disk,branch,route_layer));break
        if candidates:break
    if not candidates:raise RuntimeError('No placement for '+refname+' '+label)
    _,c,ps,disk,branch,route_layer=min(candidates,key=lambda z:z[0])
    x,y=xy(c);fpuid='75f3445ef18c4c8f950d27411e5b3797'
    head=f'LIB~{num(x)}~{num(y)}~package`REEFWING_TP_D150`nameAlias`Value`Value`{label}`Manufacturer`PCB copper / not assembled`~0~~{uid()}~1~{fpuid}~~0~~no~~'
    prefix=f'TEXT~P~{num(x)}~{num(y-4)}~0.6~0~~3~~3~{refname}~~none~{uid()}~~0~'
    pad=f'PAD~ELLIPSE~{num(x)}~{num(y)}~{num(1.5/U)}~{num(1.5/U)}~1~{net}~1~0~~0~{uid()}~0~~Y~0~-393.70079~{num(.075/U)}~{num(x)},{num(y)}'
    pcb['shape'].append('#@$'.join([head,prefix,pad]))
    pcb['shape'].append(f'TRACK~{num(.2/U)}~{route_layer}~{net}~{nativepts(ps)}~{uid()}~0')
    objects.extend([dict(g=disk,net=net,layer=1,ref=refname+'.1',pad=True,center=c),dict(g=branch,net=net,layer=route_layer,ref=refname+'_branch',pad=False)])
    if route_layer==2:
        viaid=uid()
        pcb['shape'].append(f'VIA~{num(x)}~{num(y)}~{num(.6/U)}~{net}~{num(.15/U)}~{viaid}~0')
        objects.extend(dict(g=Point(c).buffer(.3,quad_segs=24),net=net,layer=l,ref=viaid,via=True,pad=False) for l in [1,2])
    testpoints.append(dict(route_layer=route_layer,ref=refname,label=label,net=net,anchor=anchor,position_mm=c,diameter_mm=1.5))
    print(refname,label,c,flush=True)
    # Add a separate labelled schematic bank. Explicit net labels remove
    # reliance on autogenerated LED resistor-to-anode net names.
    sx=80+(index-1)%5*290;sy=1190+(index-1)//5*100
    ss.append(f'LIB~{sx}~{sy}~package`REEFWING_TP_D150`nameAlias`Value`Value`{label}`pre`TP?~0~0~{uid()}~{fpuid}~~0~~yes~no#@$T~P~{sx}~{sy-24}~0~#17324D~~9pt~~~~comment~{refname}~1~start~{uid()}~0#@$T~N~{sx}~{sy-12}~0~#17324D~~8pt~~~~comment~TEST PAD~0~start~{uid()}~0#@$E~{sx}~{sy}~5~5~#880000~1~0~none~{uid()}~0#@$P~show~0~1~{sx-20}~{sy}~180~{uid()}~0^^{sx-20}~{sy}^^M {sx-20} {sy} h 15~#880000^^0~{sx}~{sy}~0~1~start~~7pt^^0~{sx-12}~{sy-4}~0~1~middle~~6pt^^0~{sx-5}~{sy}^^0~M {sx-5} {sy}')
    ss.append(f'N~{sx-20}~{sy}~0~#0000FF~{net}~{uid()}~end~{sx-24}~{sy-3}~~7pt~0')

# Name LED anode nets in the schematic to match the PCB.
for a in list(ss):
    if not a.startswith('LIB~'):continue
    q=a.split('#@$');r=ref(q,True)
    if re.fullmatch(r'R[1-9]',r):
        b=next(b for b in q if b.startswith('P~') and b.split('^^')[0].split('~')[3]=='2');t=b.split('^^')[0].split('~');x,y=t[4:6]
        ss.append(f'N~{x}~{y}~0~#0000FF~{r}_2~{uid()}~start~{float(x)+4}~{float(y)-3}~~7pt~0')
ss.append(f'T~L~70~1130~0~#17324D~~10pt~~~~comment~REV D: D1-D9 pin 1=A, pin 2=K. GPIO -> 1k -> A; K -> GND. Test pads: Gx=GPIO, Ax=anode.~1~start~{uid()}~0')
ss.append(f'T~L~70~1152~0~#17324D~~9pt~~~~comment~TP pads: 1.5 mm copper, exposed mask, no paste / no assembly. Measure V(Gx)-V(Ax) across 1k for LED current.~1~start~{uid()}~0')

# Remove silkscreen from all exposed pads with 0.15 mm clearance.
# Keep original back branding/QR; only the front silk needs probe-pad relief.
mask=unary_union([o['g'].buffer(.24) for o in objects if o['pad'] and o['layer']==1])
def clip_shape(a):
    t=a.split('~');k=t[0];g=None
    if k=='SOLIDREGION' and t[1]=='3':g=pathpoly(t[3])
    elif k=='TRACK' and t[2]=='3':g=LineString([mm(*p) for p in points(t[4])]).buffer(float(t[1])*U/2)
    if g is None or not g.intersects(mask):return [a]
    g=g.difference(mask);out=[]
    for poly in ([g] if g.geom_type=='Polygon' else getattr(g,'geoms',[])):
        if poly.geom_type!='Polygon' or poly.area<.00001:continue
        contours=[list(poly.exterior.coords)]+[list(z.coords) for z in poly.interiors]
        out.extend(solid(v) for v in split_contours(contours))
    return out
new=[]
for a in pcb['shape']:
    if a.startswith('LIB~'):
        q=a.split('#@$');q=[q[0]]+[v for b in q[1:] for v in clip_shape(b)];new.append('#@$'.join(q))
    else:new.extend(clip_shape(a))
pcb['shape']=new
# Replace component reference lettering with a consistent, collision-checked
# label layout. Decorative neural-network lines are relieved behind labels.
label_jobs=[]
new=[]
for a in pcb['shape']:
    if a.startswith('LIB~'):
        q=a.split('#@$');r=ref(q)
        if not r.startswith('TP') and r!='L1':
            h=q[0].split('~');label_jobs.append((r,mm(h[1],h[2]),1.0))
        q=[q[0]]+[b for b in q[1:] if not b.startswith(('TEXT~P~','TEXT~N~'))]
        # Preserve hidden native reference for EasyEDA identity / BOM.
        h=a.split('#@$')[0].split('~')
        q.append(f'TEXT~P~{h[1]}~{h[2]}~0.6~0~~3~~3~{r}~~none~{uid()}~~0~')
        new.append('#@$'.join(q))
    else:new.append(a)
pcb['shape']=new
label_jobs.extend((t['label'],t['position_mm'],.85) for t in testpoints)
occupied=[box(40.5,42.7,46.1,44.3),box(53,42.7,59.7,44.3),box(66.7,42.7,73.6,44.3),box(24,46,32.5,47.3)];label_shapes=[]
for label,(x,y),height in label_jobs:
    found=False
    offsets=[(-.8,-2.5),(1.15,-.4),(-1.15-len(label)*.75,-.4),(-.5,1.2),(-.5,-2.1)]
    offsets.extend((radius*math.cos(math.radians(a)),radius*math.sin(math.radians(a))) for radius in np.arange(1.5,6,.5) for a in range(0,360,30))
    for dx,dy in offsets:
        shapes=letters(label,x+dx,y+dy,height);gs=[pathpoly(a.split('~')[3]) for a in shapes];union=unary_union(gs);rect=union.envelope.buffer(.18)
        if rect.intersects(mask) or rect.intersects(bodyunion) or any(rect.intersects(g) for g in occupied) or not box(8,8.5,77,46.5).contains(rect):continue
        label_shapes.extend(shapes);occupied.append(rect);found=True;break
    if not found:raise RuntimeError('No silk label placement for '+label)
mask=unary_union([mask]+occupied[4:])
new=[]
for a in pcb['shape']:
    if a.startswith('LIB~'):
        q=a.split('#@$');new.append('#@$'.join([q[0]]+[v for b in q[1:] for v in clip_shape(b)]))
    else:new.extend(clip_shape(a))
pcb['shape']=new+label_shapes+letters('REV D',9,45.1,.9)
# Update the existing back-side revision line without changing logo or QR.
pcb['shape']=[a for a in pcb['shape'] if not (a.startswith('SOLIDREGION~4~') and box(49.5,44.8,77.2,46.4).contains(pathpoly(a.split('~')[3]))) ]
for a in letters('REEFWING / REV D',8,45,1.1):
    t=a.split('~');t[1]='4';ps=[(85-x,y) for x,y in [mm(*v) for v in points(t[3])]]
    t[3]='M '+' L '.join(' '.join(num(v) for v in xy(p)) for p in ps)+' Z';pcb['shape'].append('~'.join(t))

(ROOT/'Reefwing-NFC-Card-RevD.json').write_text(json.dumps(sch,ensure_ascii=False,indent=2)+'\n')
(ROOT/'Reefwing-PCB-RevD.json').write_text(json.dumps(pcb,ensure_ascii=False,indent=2)+'\n')
(HERE/'test-points.json').write_text(json.dumps(testpoints,indent=2)+'\n')
(HERE/'source-hashes.json').write_text(json.dumps({f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in ['Reefwing-NFC-Card-RevC.json','Reefwing-PCB-RevC.json']},indent=2)+'\n')
print('Rev D native files written; run independent validation before use.')
