"""Convert compound polygon contours into simple trapezoids (even-odd fill).
Avoid relying on unsupported holes in EasyEDA solid regions.
"""
def split_contours(contours):
 bounds=[(min(p[0] for p in c),min(p[1] for p in c),max(p[0] for p in c),max(p[1] for p in c)) for c in contours]
 parents=list(range(len(contours)))
 def root(i):
  while parents[i]!=i:i=parents[i]
  return i
 for i,a in enumerate(bounds):
  for j,b in enumerate(bounds[:i]):
   if a[0]<=b[2] and b[0]<=a[2] and a[1]<=b[3] and b[1]<=a[3]:parents[root(i)]=root(j)
 groups={}
 for i,c in enumerate(contours):groups.setdefault(root(i),[]).append(c)
 for cs in groups.values():
  yy=sorted({v[1] for c in cs for v in c});edges=[(a,b) for c in cs for a,b in zip(c,c[1:]+c[:1]) if abs(a[1]-b[1])>1e-9]
  for lo,hi in zip(yy,yy[1:]):
   if hi-lo<1e-8:continue
   mid=(lo+hi)/2
   active=[(a,b) for a,b in edges if min(a[1],b[1])<mid<max(a[1],b[1])]
   def xx(e,y):
    a,b=e;return a[0]+(y-a[1])*(b[0]-a[0])/(b[1]-a[1])
   active.sort(key=lambda e:xx(e,mid))
   assert len(active)%2==0
   for a,b in zip(active[::2],active[1::2]):
    if xx(b,mid)-xx(a,mid)<1e-8:continue
    yield [(xx(a,lo),lo),(xx(b,lo),lo),(xx(b,hi),hi),(xx(a,hi),hi)]
