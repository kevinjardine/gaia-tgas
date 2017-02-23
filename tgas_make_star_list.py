import math
import ephem
import sys
import os

#config

rootDir = 'd:/projects/astronomy/tgas/'

#code

errLimit = 0.2
colourLimit = 0.0
magLimit = 3

colour = {}
colourHip = {}
tychoColourErrorCount = 0
tychoColourCount = 0
missingHipparcosCount = 0
missingColourIndex = 0
negativeParallaxCount = 0
highErrorCount = 0
meanCount = 0
tychoNames = {}
hipNames = {}
tychoCount = 0
tgasCount = 0
hipCount = 0
hipTGASCount = 0
trueHIPCount = 0
hipsList = []
hipStars = {}

starCounts = {'I':{'above':0,'below':0},'II':{'above':0,'below':0},'III':{'above':0,'below':0},'IV':{'above':0,'below':0}}
tgasStarCounts = {'I':{'above':0,'below':0},'II':{'above':0,'below':0},'III':{'above':0,'below':0},'IV':{'above':0,'below':0}}
starCountsHot = {'I':{'above':0,'below':0},'II':{'above':0,'below':0},'III':{'above':0,'below':0},'IV':{'above':0,'below':0}}

if not os.path.isdir(rootDir+'output/star_list'):
    os.mkdir(rootDir+'output/star_list')

csv = open(rootDir+'output/star_list/stars.csv','w')

fp = open(rootDir+'data/hipparcos/hip2.csv','r')
fieldNames = fp.readline().strip().split(',')
fieldTypes = fp.readline().strip().split(',')
fp.readline()
line = fp.readline()
while len(line) != 0:
    hipCount += 1
    data = {}
    bits = line.strip().split(',')
    for i in range(0,len(bits)):
        data[fieldNames[i]] = bits[i]
    if data['B-V'].strip() != '':
        colourIndex = float(data['B-V'])
        hipStars[data['HIP']] = colourIndex
    line = fp.readline()
fp.close()

for tychoSection in range(0,20):
    fp = open(rootDir+'data/tycho/tyc2.dat.'+str(tychoSection).zfill(2),'r')
    line = fp.readline()
    while len(line) != 0:
        bits = line.strip().split('|')
        hip = line[142:148].strip()
        if bits[17].strip() == '':
            if hip != '':
                hipsList.append(hip)
        else:
            nameBits = bits[0].split(' ')
            name = str(int(nameBits[0].strip()))+'-'+str(int(nameBits[1].strip()))+'-'+str(int(nameBits[2].strip()))
            
            tychoNames[name] = True
            if hip != '':
                hipNames[hip] = True
            else:
                tychoCount += 1
            if bits[2].strip() != '':
                ra = float(bits[2])*math.pi/180
                dec = float(bits[3])*math.pi/180
                np = ephem.Equatorial(ra,dec,epoch='2000')
            else:
                ra = float(bits[24])*math.pi/180
                dec = float(bits[25])*math.pi/180
                np = ephem.Equatorial(ra,dec,epoch='1990')
            
            g = ephem.Galactic(np)
            glat = g.lat*180/math.pi
            glon = g.lon*180/math.pi

            if glat >= 0:
                region = 'above'
            else:
                region = 'below'

            if glon < 90:
                quadrant = 'I'
            elif glon < 180:
                quadrant = 'II'
            elif glon < 270:
                quadrant = 'III'
            else:
                quadrant = 'IV'

            starCounts[quadrant][region] += 1
            if (bits[17].strip() != '') and (bits[19].strip() != ''):
                btmag = float(bits[17])
                vtmag = float(bits[19])
                bTvT = btmag - vtmag
                colourIndex = 0.85*bTvT
                if hip != '':
                    colourHip[hip] = colourIndex
                else:
                    colour[name] = colourIndex
            
            tychoColourCount += 1
        
        line = fp.readline()
    fp.close()

fp = open(rootDir+'data/tycho/suppl_1.dat','r')
line = fp.readline()
while len(line) != 0:
    hip = line[115:121].strip()
    if line[83:89].strip() == '':
        if hip != '':
            hipsList.append(hip)
    else:
        bits = line.strip().split('|')
        nameBits = bits[0].split(' ')
        name = str(int(nameBits[0].strip()))+'-'+str(int(nameBits[1].strip()))+'-'+str(int(nameBits[2].strip()))
        if (line[83:89].strip() != '') and (line[96:102].strip() != ''):
            btmag = float(line[83:89].strip())
            vtmag = float(line[96:102].strip())
            bTvT = btmag - vtmag
            
            colourIndex = 0.85*bTvT
            if hip != '':
                colourHip[hip] = colourIndex
            else:
                colour[name] = colourIndex
        tychoNames[name] = True
        if hip != '':
            hipNames[hip] = True
        else:
            tychoCount += 1
            #print('hip',hip)
        ra = float(bits[2])*math.pi/180
        dec = float(bits[3])*math.pi/180
        np = ephem.Equatorial(ra,dec,epoch='1991.25')
        g = ephem.Galactic(np)
        glat = g.lat*180/math.pi
        glon = g.lon*180/math.pi
        if glat >= 0:
            region = 'above'
        else:
            region = 'below'

        if glon < 90:
            quadrant = 'I'
        elif glon < 180:
            quadrant = 'II'
        elif glon < 270:
            quadrant = 'III'
        else:
            quadrant = 'IV'

        starCounts[quadrant][region] += 1
        
        tychoColourCount += 1
    
    line = fp.readline()

fp.close()

tgas = {}

for tgasNum in range(0,16):
    fp = open(rootDir+'data/tgas/TgasSource_000-000-'+str(tgasNum).zfill(3)+'.csv','r')
    fieldNames = fp.readline().strip().split(',')
    line = fp.readline()
    while len(line) != 0:
        tgasCount += 1
        fromHIPStars = False
        data = {}
        bits = line.strip().split(',')
        for i in range(0,len(bits)):
            data[fieldNames[i]] = bits[i]

        tyc = data['tycho2_id']
        if tyc != '':
            name = 'TYC '+tyc
            #if tyc not in tychoNames:
                #print(tyc)
        plx = float(data['parallax'])
        err = float(data['parallax_error'])
        fratio = err/plx
        if fratio < errLimit:
            hip = data['hip']
            if hip != '':
                name = 'HIP '+hip
                if hip in hipsList:
                    hipTGASCount += 1

                if hip not in hipNames:
                    missingHipparcosCount += 1
            colourIndex = 1000
            if hip in colourHip:
                colourIndex = colourHip[hip]
            elif tyc in colour:
                colourIndex = colour[tyc]
            elif hip in hipStars:
                colourIndex = hipStars[hip]
                fromHIPStars = True
            else:
                missingColourIndex += 1 

            glon = float(data['l'])
            glat = float(data['b'])  
            if glat >= 0:
                region = 'above'
            else:
                region = 'below'

            if glon < 90:
                quadrant = 'I'
            elif glon < 180:
                quadrant = 'II'
            elif glon < 270:
                quadrant = 'III'
            else:
                quadrant = 'IV'
            tgasStarCounts[quadrant][region] += 1
            if plx > 0:
                if fromHIPStars:
                    trueHIPCount += 1
                    #print('HIP '+hip)          
                relMag = float(data['phot_g_mean_mag'])
                dist = 1000/plx
                cosl = math.cos(glon*math.pi/180)
                sinl = math.sin(glon*math.pi/180)
                cosb = math.cos(glat*math.pi/180)
                sinb = math.sin(glat*math.pi/180)
                xg = dist*cosb*cosl
                yg = dist*cosb*sinl
                zg = dist*sinb
                
                m = relMag - 5*(math.log10(dist) - 1)
                if colourIndex <= colourLimit:
                    isHot = 1
                else:
                    isHot = 0 

                if m <= magLimit:
                    isBright = 1
                else:
                    isBright = 0
                
                csv.write(','.join([name, str(colourIndex), str(xg), str(yg), str(zg), data['l'],data['b'],str(m),data['parallax'],data['pmra'],data['pmdec'],str(isHot),str(isBright)])+"\n")
            else:
                negativeParallaxCount += 1          
        else:
            highErrorCount += 1
        line = fp.readline()
    fp.close()

csv.close()

print('hipCount',hipCount)
print('tychoCount',tychoCount)
print('tgasCount',tgasCount)
print('missingColourIndex', missingColourIndex)
print('negativeParallaxCount', negativeParallaxCount)
print('highErrorCount', highErrorCount)

print('starCounts',starCounts)
print('tgasStarCounts',tgasStarCounts)
