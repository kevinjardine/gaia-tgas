import sys
import os

#config

rootDir = 'd:/projects/astronomy/tgas/'

#code

argv = sys.argv

if argv[1] == 'hot':
    isoList = range(40,100,5)
    isoType = 'hot'
    labelPrefix = 'TR1'
elif argv[1] == 'bright':
    isoList = [85,90,95,97]
    isoType = 'bright'
    labelPrefix = 'TR2'

svgBegin = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" height="8192" width="8192" viewBox="0 0 8192 8192">
"""

svgImage = """
<image
     y="0"
     x="0"
     id="imageortho"
     xlink:href="file:///%(fn)s"
     preserveAspectRatio="none"
     height="8192"
     width="8192" />
"""

svgTextTemplate = """
<text
     xml:space="preserve"
     text-anchor="middle"
     style="font-style:normal;font-weight:normal;font-family:Arial;letter-spacing:0px;word-spacing:0px;fill-opacity:1;stroke:none;stroke-width:1px;stroke-linecap:butt;stroke-linejoin:miter;stroke-opacity:1"
     x="%(x)s"
     y="%(y)s"><tspan
       x="%(x)s"
       y="%(y)s"
       style="font-size:%(size)spx;fill:#ffff00">%(name)s</tspan>
</text>
"""

svgEnd = """</svg>"""

ratio = 1.25

structure = {}
structureFile = rootDir+'output/slices/'+isoType+'/structure/structure_tab.txt'
fp = open(structureFile,'r')
line = fp.readline()
while len(line) != 0:
    bits = line.split(':')
    structs = []
    for i in range(0,len(bits)-1):
        parts = bits[i].strip().split('(')[0].strip().split(' ')
        if parts[0][0] == 'T':
            structs.append(parts[0]+' '+parts[1])
        else:
            structs.append(parts[1]+' '+parts[2])
    endItem = structs[-1]
    structure[endItem] = structs[:-1]
    line = fp.readline()

svgDir = rootDir+'output/slices/'+isoType+'/svg/'
if not os.path.isdir(svgDir):
        os.mkdir(svgDir)

gp = open(svgDir+'stack_ortho.svg','w')
gp.write(svgBegin+"\n")
gp.write(svgImage % {'fn':rootDir+'output/slices/'+isoType+'/iso/renders/ortho/stack.png'})

for iso in isoList:
    fp = open(rootDir+'output/slices/'+isoType+'/csv/regions_'+str(iso)+'.csv','r')
    line = fp.readline()
    while len(line) != 0:
        bits = line.strip().split(',')
        if len(bits) > 1:
            region,polycount,regionLength,x,y,z,xmin,xmax,ymin,ymax,zmin,zmax,count,hCount,bCount = bits
            hCount = int(hCount)
            bCount = int(bCount)
            if (isoType == 'hot' and int(hCount) >= 5) or (isoType == 'bright' and int(bCount) >= 5):                
                label = labelPrefix+' '+str(iso)+'-'+region
                if label in structure:
                    xr = float(x)
                    yr = float(y)
                    x = 8192-int((2*(float(xr)-408)+800)*(8192/1600)) + 1024
                    y = int((2*(float(yr)-399)+800)*(8192/1600)) + 1024
                    gp.write(svgTextTemplate % {'x':x/ratio, 'y':y/ratio,'name':label,'size':'8'})
        line = fp.readline()
    fp.close()

gp.write(svgEnd+"\n")
gp.close()