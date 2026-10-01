"""Sample native circular SVG arcs for silkscreen clearance checks."""
import re,math
from shapely.geometry import LineString
def geometry(t,bx=4047.559,by=3046.343,u=.254):
 v=list(map(float,re.findall(r'-?\d+(?:\.\d+)?',t[4])))
 x0,y0,rx,ry,rotation,large,sweep,x1,y1=v
 assert abs(rx-ry)<.001,'Only circular arcs supported'
 dx=x1-x0;dy=y1-y0;d=math.hypot(dx,dy);r=max(rx,d/2);h=math.sqrt(max(0,r*r-d*d/4))
 for sign in [1,-1]:
  cx=(x0+x1)/2-sign*dy/d*h;cy=(y0+y1)/2+sign*dx/d*h
  a=math.atan2(y0-cy,x0-cx);b=math.atan2(y1-cy,x1-cx);delta=(b-a)%(2*math.pi) if sweep else -((a-b)%(2*math.pi))
  if (abs(delta)>math.pi)==bool(large):break
 ps=[((cx+r*math.cos(a+delta*i/64)-bx)*u,(cy+r*math.sin(a+delta*i/64)-by)*u) for i in range(65)]
 return LineString(ps).buffer(float(t[1])*u/2)
