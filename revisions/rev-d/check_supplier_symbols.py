"""Audit placed supplier pin definitions and linked physical pad geometry."""
import json,math,hashlib
from pathlib import Path
P=Path(__file__).resolve().parent;R=P.parents[1]
sch=json.load(open(R/'Reefwing-NFC-Card-RevD.json'))['schematics'][0]['dataStr']['shape'];pcb=json.load(open(R/'Reefwing-PCB-RevD.json'))['shape']
symbols={next(b.split('~')[12] for b in q if b.startswith('T~P~')):q for a in sch if a.startswith('LIB~') for q in [a.split('#@$')]}
footprints={next(b.split('~')[10] for b in q if b.startswith('TEXT~P~')):q for a in pcb if a.startswith('LIB~') for q in [a.split('#@$')]}
manifest=json.load(open(P/'supplier-symbols.json'))
assert len(manifest)==26 and sum(m['populated'] for m in manifest)==25
for m in manifest:
 path=R/'libraries'/f"{m['code']}-symbol.json";source=json.load(open(path));q=symbols[m['ref']];h=q[0].split('~');dx,dy=m['offset']
 assert hashlib.sha256(path.read_bytes()).hexdigest()==m['source_sha256']
 assert h[7]==source['head']['puuid'] and h[8]==source['head']['uuid']
 sp={a.split('^^')[0].split('~')[3]:a.split('^^') for a in source['shape'] if a.startswith('P~')}
 ap={a.split('^^')[0].split('~')[3]:a.split('^^') for a in q if a.startswith('P~')}
 assert set(sp)==set(ap)
 for pin,z in sp.items():
  v=ap[pin];s=z[0].split('~');a=v[0].split('~')
  assert [s[i] for i in [1,2,3,6,8]]==[a[i] for i in [1,2,3,6,8]],(m['ref'],pin,'electrical metadata')
  assert math.dist((float(a[4]),float(a[5])),(float(s[4])+dx,float(s[5])+dy))<1e-6
  for index in [3,4]:
   s=z[index].split('~');a=v[index].split('~');assert s[:1]+s[3:]==a[:1]+a[3:],(m['ref'],pin,'name/number')
 assert len([b for b in q[1:] if not b.startswith('T~')])==len(source['shape'])
 f=footprints[m['ref']];fh=f[0].split('~');assert fh[8]==source['head']['puuid'],(m['ref'],fh[8],source['head']['puuid'])
 fp=json.load(open(R/'libraries'/f"{m['code']}-footprint.json"));assert fp['head']['uuid']==fh[8]
 fs={b.split('~')[8]:b.split('~') for b in fp['shape'] if b.startswith('PAD~')};actual={b.split('~')[8]:b.split('~') for b in f if b.startswith('PAD~')}
 assert set(fs)==set(actual)
 sign=-1 if float(fh[4] or 0)==180 else 1
 for pin,s in fs.items():
  a=actual[pin];sx=(float(s[2])-float(fp['head']['x']))*sign+float(fh[1]);sy=(float(s[3])-float(fp['head']['y']))*sign+float(fh[2])
  assert math.dist((sx,sy),(float(a[2]),float(a[3])))*.254<.005,(m['ref'],pin,'land position')
  assert a[1]==s[1] and a[6]==s[6] and abs(float(a[4])-float(s[4]))<.001 and abs(float(a[5])-float(s[5]))<.001,(m['ref'],pin,'land dimensions')
report={'status':'PASS','supplier_instances':26,'populated_instances':25,'part_codes':sorted({m['code'] for m in manifest}),'checks':['Placed pin numbers, names, electrical types and relative positions match saved supplied symbols.','Symbol UUID and linked footprint UUID match source definitions.','PCB pad numbers, shapes, sizes and positions match linked footprints after placement rotation.','C1 uses supplied capacitor graphics as DNP without assigning a purchased part.'],'note':'Supplier snapshots are versioned; this is not a fresh stock check or native EasyEDA ERC/DRC.'}
(P/'supplier-validation.json').write_text(json.dumps(report,indent=2)+'\n');print('PASS: supplied symbols and linked footprint pads for all 25 populated parts plus DNP C1')
