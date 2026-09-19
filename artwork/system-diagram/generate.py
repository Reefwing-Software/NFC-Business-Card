"""Generate an editable, article-ready SVG system diagram (no external packages)."""
from pathlib import Path
from html import escape
P = Path(__file__).resolve().parent
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="1120" viewBox="0 0 1800 1120">']
s.append('''<defs><style>text{font-family:Arial,Helvetica,sans-serif;fill:#183049} .small{font-size:19px}</style>''')
for name, color in [('power','#d88715'),('data','#168ba0'),('control','#7754b5'),('gpio','#32906c')]:
    s.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="{color}"/></marker>')
s.append('</defs>')
def rect(x,y,w,h,fill,stroke='none',r=18):
    s.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
def text(x,y,t,size=22,weight=400,color='#183049',anchor='start'):
    s.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" style="fill:{color}" text-anchor="{anchor}">{escape(t)}</text>')
def line(points,kind='data',both=False,dash=False,arrow=True):
    colors={'power':'#d88715','data':'#168ba0','control':'#7754b5','gpio':'#32906c'}
    attrs=f' marker-end="url(#{kind})"' if arrow else ''
    if both: attrs+=f' marker-start="url(#{kind})"'
    if dash: attrs+=' stroke-dasharray="9 7"'
    s.append(f'<polyline points="{points}" fill="none" stroke="{colors[kind]}" stroke-width="4" stroke-linejoin="round"{attrs}/>')
rect(0,0,1800,1120,'#f5f8fc',r=0)
text(50,65,'REEFWING  /  NFC BUSINESS CARD',19,700,'#168ba0')
text(50,120,'A battery-free card with a neural-network light show',40,700)
text(50,161,'System block diagram • Rev C prototype • Functional connections, not a wiring schematic',22,color='#617185')
# Power rail, with explicit isolation bridge.
line('850,340 850,230 985,230','power')
rect(985,198,110,64,'#fff2d9','#d88715',12)
text(1040,237,'JP1',25,700,anchor='middle')
line('1095,230 1295,230 1295,340','power')
line('1160,230 1160,285 865,285','power',arrow=False)
s.append('<path d="M865 285 Q850 255 835 285" fill="none" stroke="#d88715" stroke-width="4"/>')
line('835,285 650,285 650,340','power')
text(635,217,'Harvested power',21,700,'#a66508')
text(1177,211,'VDD rail',21,700,'#a66508')
text(635,323,'VCC',18,700,'#a66508',anchor='end')
text(830,323,'VOUT',18,700,'#a66508')
text(1308,323,'VDD',18,700,'#a66508')
# Phone and antenna.
rect(50,370,195,270,'#eaf1fc','#a6badd')
text(147,417,'NFC phone',25,700,anchor='middle')
rect(107,443,80,115,'#fff','#7c97c0',12)
text(147,490,'NFC',21,700,anchor='middle')
text(147,535,'↗',30,700,anchor='middle')
text(147,599,'Reads URL',20,anchor='middle')
line('245,485 315,485','data',both=True,dash=True)
text(280,451,'RF',18,700,anchor='middle')
rect(315,370,215,270,'#e7f5f6','#88c6cd')
text(422,417,'PCB antenna',24,700,anchor='middle')
for i in range(4): rect(352+i*7,446+i*7,140-i*14,91-i*14,'none','#168ba0',10)
text(422,575,'L1 • four turns',20,anchor='middle')
text(422,609,'C1: tuning / DNP',19,anchor='middle')
line('530,485 600,485','data',both=True)
text(565,451,'LA / LB',16,700,anchor='middle')
text(55,686,'13.56 MHz • RF energy + bidirectional NFC data',21,700,'#168ba0')
# NTAG block.
rect(600,340,350,350,'#fff','#168ba0')
rect(602,342,346,76,'#ddf3f5',r=16)
text(625,374,'U1  /  NXP NTAG I²C plus',20,700)
text(625,402,'NT3H2111',26,700)
for y,title,sub in [(454,'RF interface + rectifier','NFC Forum Type 2 Tag'),(535,'EEPROM + NDEF URI','Stores the website address'),(616,'I²C interface + FD output','Energy harvesting on VOUT')]:
    text(625,y,title,22,700)
    text(625,y+28,sub,19,color='#617185')
# Digital links.
line('950,468 1120,468','data',both=True)
text(1035,420,'I²C',23,700,'#168ba0',anchor='middle')
text(1035,447,'SDA / SCL',18,anchor='middle')
text(1035,500,'PA1 / PA2',18,anchor='middle')
line('950,583 1120,583','control')
text(1035,552,'FD → PA3',21,700,'#7754b5',anchor='middle')
text(1035,618,'Open-drain',17,anchor='middle')
text(1035,642,'100 kΩ pull-up',17,anchor='middle')
# MCU and LEDs.
rect(1120,340,350,350,'#fff','#7754b5')
rect(1122,342,346,76,'#ede7f7',r=16)
text(1145,374,'U2  /  Microchip tinyAVR',20,700)
text(1145,402,'ATtiny816',26,700)
for y,title,sub in [(454,'8-bit AVR CPU','1 MHz in this project'),(535,'8 KB Flash • 512 B SRAM','Animation + URL writer sketches'),(616,'RTC + GPIO + TWI + UPDI','Sleeps between animation steps')]:
    text(1145,y,title,22,700)
    text(1145,y+28,sub,18,color='#617185')
line('1470,485 1550,485','gpio')
text(1510,453,'GPIO',17,700,'#32906c',anchor='middle')
rect(1550,370,200,270,'#e8f5ed','#8ec5a6')
text(1650,414,'9 red LEDs',24,700,anchor='middle')
for col,ys in enumerate([[470,510,550],[450,490,530,570],[485,535]]):
    for y in ys:s.append(f'<circle cx="{1595+col*55}" cy="{y}" r="9" fill="#ed6b56"/>')
text(1650,606,'1 kΩ per LED',20,anchor='middle')
text(1445,726,'PA4–PA7 / PB0–PB4',19,700,'#32906c')
text(1517,755,'One LED on at a time',18,color='#617185')
# Lower mode cards and programmer interface.
rect(50,780,910,205,'#fff','#dbe4ee')
text(75,819,'TWO OPERATING MODES',20,700,'#168ba0')
text(75,859,'NFC use: JP1 closed; the phone powers the card.',23,700)
text(75,891,'VOUT typically provides 2 V at 5 mA with an NFC phone.*',21)
text(75,930,'Programming: JP1 open; external 3 V powers both ICs.',23,700)
text(75,962,'Keep the card away from NFC readers while programming.',21)
rect(1090,840,540,145,'#fff2d9','#d88715')
text(1115,879,'J1  /  Three pogo programming pads',23,700)
text(1115,917,'GND • 3V0 / VDD • UPDI',22)
text(1115,951,'Adafruit UPDI Friend set to 3 V',21,color='#617185')
line('1210,840 1210,690','control')
text(1192,784,'UPDI / PA0',18,700,'#7754b5',anchor='end')
line('1380,840 1380,690','power')
text(1396,790,'3 V → VDD rail',18,700,'#a66508')
# Footer legend and caveats.
for x,kind,label in [(50,'power','Power'),(235,'data','RF / I²C data'),(485,'control','Control / programming'),(845,'gpio','LED drive')]:
    line(f'{x},1030 {x+45},1030',kind,arrow=False)
    text(x+57,1037,label,19)
text(50,1075,'*Harvested output depends on field strength, antenna and distance. All blocks share GND; decoupling and bus pull-ups omitted.',18,color='#617185')
text(50,1103,'Sources: NXP NT3H2111/2211 §§6, 8.6; Microchip DS40002288A §§2–5; Reefwing Rev C schematic and firmware.',17,color='#617185')
s.append('</svg>')
(P/'reefwing-nfc-system.svg').write_text('\n'.join(s))
