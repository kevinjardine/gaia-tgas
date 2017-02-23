import math
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
<svg xmlns="http://www.w3.org/2000/svg" version="1.1" height="2880" width="5760" viewBox="0 0 5760 2880">
"""

svgImage = """
<image
     y="0"
     x="0"
     id="image7691"
     xlink:href="file:///%(fn)s"
     preserveAspectRatio="none"
     height="2880"
     width="5760" />
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

svgDir = rootDir+'output/slices/'+isoType+'/svg/'
if not os.path.isdir(svgDir):
        os.mkdir(svgDir)

gp = open(svgDir+'stack_pan.svg','w')
gp.write(svgBegin+"\n")
gp.write(svgImage % {'fn':rootDir+'output/slices/'+isoType+'/iso/renders/pan/stack.png'})

clusterCount = 0
fp = open(rootDir+'data/kharchenko/catalog_stripped.txt','r')
line = fp.readline()
line = fp.readline()
while len(line) != 0:
    data = {}
    bits = line.strip().split('|')
    if len(bits) > 1:
        name = bits[1].strip()
        glonglat = bits[5].strip()
        #print(glonglat)
        glon = float(glonglat.split(' ')[0].strip())
        glat = float(glonglat.split(' ')[-1].strip())
        r = bits[8].strip()
        dist = bits[18].strip()
        if r != '':
            r = 16*float(r)
            if dist != '':
                name += ' ['+str(int(float(dist)))+' pc]'
                dist = float(dist)
                if dist <= 800:
                    clusterCount += 1
                    x = (5760-int(float(glon)*16))+2880
                    if x > 5760:
                        x -= 5760
                    y = 2880 - (int(float(glat)*16)+1440)
                    cluster = "<circle r='%(r)s' cx='%(px)s' cy='%(py)s' fill='none' stroke-width='1' stroke='orange'>" % {'r':r,'px':x, 'py':y}
                    cluster += "<title>"+name+"</title></circle>"
                    gp.write(cluster+"\n")
                    gp.write(svgTextTemplate % {'x':x, 'y':y+r+4,'name':name.replace('_',' '),'size':'2'})
    line = fp.readline()
fp.close()
print('clusterCount',clusterCount)

# add Hyades (twice for each side) as it is not in Kharchenko data
glon = 180.06
glat = -22.34
r = 5.5
name = 'Hyades'
x = (5760-int(float(glon)*16))+2880
if x > 5760:
    x -= 5760
y = 2880 - (int(float(glat)*16)+1440)
r = 16*float(r)
cluster = "<circle r='%(r)s' cx='%(px)s' cy='%(py)s' fill='none' stroke-width='1' stroke='orange'>" % {'r':r,'px':x, 'py':y}
cluster += "<title>"+name+"</title></circle>"
gp.write(cluster+"\n")
gp.write(svgTextTemplate % {'x':x, 'y':y+r+4,'name':name.replace('_',' '),'size':'2'})

glon = 180.06+360
glat = -22.34
r = 5.5
name = 'Hyades'
x = (5760-int(float(glon)*16))+2880
if x > 5760:
    x -= 5760
y = 2880 - (int(float(glat)*16)+1440)
r = 16*float(r)
cluster = "<circle r='%(r)s' cx='%(px)s' cy='%(py)s' fill='none' stroke-width='1' stroke='orange'>" % {'r':r,'px':x, 'py':y}
cluster += "<title>"+name+"</title></circle>"
gp.write(cluster+"\n")
gp.write(svgTextTemplate % {'x':x, 'y':y+r+4,'name':name.replace('_',' '),'size':'2'})


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
                    xr = (float(x)-408)*2
                    yr = (float(y)-399)*2
                    zr = (float(z)-399)*2
                    rho = math.sqrt(xr*xr+yr*yr+zr*zr)
                    r = math.sqrt(xr*xr+yr*yr)
                    glat = 180*math.atan(zr/r)/math.pi
                    #glon = 180*math.atan2(yr,xr)/math.pi
                    glon = 180*math.atan2(xr,yr)/math.pi
                    
                    x = int(glon*16)
                    if x > 5760:
                        x -= 5760
                    if x < 0:
                        x += 5760
                    y = 2880 - (int(glat*16)+1440)

                    gp.write(svgTextTemplate % {'x':x, 'y':y,'name':label+' ['+str(round(rho))+' pc]','size':'4'})
        line = fp.readline()
    fp.close()
gp.write(svgEnd+"\n")
gp.close()
