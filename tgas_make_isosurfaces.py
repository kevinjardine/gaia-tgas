import vtk
import time
import sys
import os
import copy
import math

#config

rootDir = 'd:/projects/astronomy/tgas/'

#code

binSize = 2
hotSlices = False
brightSlices = False

argv = sys.argv

if argv[1] == 'hot':
    percentages = range(95,35,-5)
    sliceDir = rootDir+'output/slices/hot/16bit/'
    csvDir = rootDir+'output/slices/hot/csv/'
    isoDir = rootDir+'output/slices/hot/iso/'
    hotSlices = True
elif argv[1] == 'bright':
    percentages = [97,95,90,85]
    sliceDir = rootDir+'output/slices/bright/16bit/'
    csvDir = rootDir+'output/slices/bright/csv/'
    isoDir = rootDir+'output/slices/bright/iso/'
    brightSlices = True

if not os.path.isdir(csvDir):
    os.mkdir(csvDir)

if not os.path.isdir(isoDir):
    os.mkdir(isoDir)

fp = open(rootDir+'output/star_list/stars.csv','r')
line = fp.readline()
stars = {}
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        name, colourIndex, xg, yg, zg, glon, glat, m, plx, pmra, pmdec, isHot, isBright = bits
        stars[name] = {'line':line.strip(),'ci':colourIndex,'center':[float(xg),float(yg),float(zg)],'isHot':isHot,'isBright':isBright}
    line = fp.readline()
fp.close()

if brightSlices:
    clusters = {}
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
            if dist != '':
                dist = int(float(dist))
                if dist <= 800:
                    cosl = math.cos(glon*math.pi/180)
                    sinl = math.sin(glon*math.pi/180)
                    cosb = math.cos(glat*math.pi/180)
                    sinb = math.sin(glat*math.pi/180)
                    clusters[name] = []
                    for d in range(0,51,10):
                        for s in [1,-1]:
                            dist2 = dist + s*d            
                            xg = dist2*cosb*cosl
                            yg = dist2*cosb*sinl
                            zg = dist2*sinb
                            clusters[name].append([xg,yg,zg,dist,dist2])
        line = fp.readline()
    fp.close()

    #add Hyades
    dist = 47
    glon = 180.06
    glat = -22.34
    name = 'Hyades'
    cosl = math.cos(glon*math.pi/180)
    sinl = math.sin(glon*math.pi/180)
    cosb = math.cos(glat*math.pi/180)
    sinb = math.sin(glat*math.pi/180)
    clusters[name] = []
    for d in range(0,51,5):
        for s in [1,-1]:
            dist2 = dist + s*d            
            xg = dist2*cosb*cosl
            yg = dist2*cosb*sinl
            zg = dist2*sinb
            clusters[name].append([xg,yg,zg,dist,dist2])

#for some reason the isosurfaces are generated slightly off centre
sunPosition = [408,399,399]

#for percent in range(60,100,5):
for percent in percentages:
    starRegion = {}

    isoValue = int(65536*percent/100 + 0.5)

    reader = vtk.vtkVolume16Reader()
    reader.SetFilePrefix(sliceDir)
    reader.SetFilePattern('%sslice_%04d.pgm')
    
    reader.SetImageRange(0//binSize,(1600//binSize)-1)
    reader.SetDataSpacing(1,1,1)
    reader.SetDataDimensions (1600//binSize,1600//binSize)
    reader.Update()

    sc = vtk.vtkSliceCubes()
    sc.SetReader(reader)
    sc.SetFileName(isoDir+'iso.tri')
    sc.SetLimitsFileName(isoDir+'iso.lim')
    sc.SetValue(isoValue)
    sc.Write()
    # read from file
    mcReader = vtk.vtkMCubesReader()
    mcReader.SetFileName(isoDir+'iso.tri')
    mcReader.SetLimitsFileName(isoDir+'iso.lim')

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputConnection(mcReader.GetOutputPort())

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(800,800)
    renWin.AddRenderer(ren)
    ren.AddActor(actor)

    percentageDir = isoDir+'iso_'+str(percent)+'_percent/'
    if not os.path.isdir(percentageDir):
        os.mkdir(percentageDir)
    else:
        for f in os.listdir(percentageDir):
            os.remove(percentageDir+f) 

    writer = vtk.vtkOBJExporter()
    writer.SetFilePrefix(isoDir+'iso_'+str(percent)+'_percent')
    writer.SetInput(renWin)
    writer.Write()

    appendFilter = vtk.vtkAppendPolyData()

    connectivity = vtk.vtkPolyDataConnectivityFilter()
    connectivity.SetInputConnection(mcReader.GetOutputPort())
    connectivity.SetExtractionModeToSpecifiedRegions()
    connectivity.ScalarConnectivityOff()
    connectivity.Update()

    numberOfRegions = connectivity.GetNumberOfExtractedRegions()
    regionSizes = connectivity.GetRegionSizes()

    print(percent,'number of regions',numberOfRegions)

    setEncPts = vtk.vtkSelectEnclosedPoints()
    setEncPts.SetTolerance(.000001) 

    fp = open(csvDir+'regions_'+str(percent)+'.csv','w')
    if brightSlices:
        clusterCSV = open(csvDir+'clusters_'+str(percent)+'.csv','w')
    totalCount = 0
    for i in range(0,numberOfRegions):
        count = 0
        bCount = 0
        hCount = 0
        connectivity.InitializeSpecifiedRegionList() 
        connectivity.AddSpecifiedRegion(i)
        connectivity.Update()

        polyData = connectivity.GetOutput()
        setEncPts.Initialize(polyData)

        c = polyData.GetCenter()
        polys = polyData.GetNumberOfPolys()
        regionLength = polyData.GetLength()
        (xmin,xmax,ymin,ymax,zmin,zmax) = polyData.GetBounds()     
        
        if regionLength > 0:
            
            for starName in stars:
                p = stars[starName]['center']
                if setEncPts.IsInsideSurface(sunPosition[0]+0.5*p[1],sunPosition[1]-0.5*p[0],sunPosition[2]+0.5*p[2]) != 0:
                    starRegion[starName] = i
                    count += 1
                    if stars[starName]['isHot']  == '1':
                        hCount += 1
                    if stars[starName]['isBright']  == '1':
                        bCount += 1
            if brightSlices:
                for clusterName in clusters:
                    for p in clusters[clusterName]:
                        if setEncPts.IsInsideSurface(sunPosition[0]+0.5*p[1],sunPosition[1]-0.5*p[0],sunPosition[2]+0.5*p[2]) != 0:
                            s2 = ','.join([clusterName,str(p[3]),str(p[4]),str(i)])
                            print(s2)
                            clusterCSV.write (s2+"\n")
                            break

        if (hotSlices and hCount >= 5) or (brightSlices and bCount >= 5):
            polyData2 = vtk.vtkPolyData()
            polyData2.ShallowCopy(polyData)
            appendFilter.AddInputData(polyData2)
            appendFilter.Update()

            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputData(polyData)
            mapper.Update()

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)
            ren = vtk.vtkRenderer()
            renWin = vtk.vtkRenderWindow()
            renWin.SetSize(800,800)
            renWin.AddRenderer(ren)
            ren.AddActor(actor)

            writer = vtk.vtkOBJExporter()
            writer.SetFilePrefix(percentageDir+'region_'+str(i))
            writer.SetInput(renWin)
            writer.Write()
            
        s = ','.join(map(str,[i,polys,regionLength,c[0],c[1],c[2],xmin,xmax,ymin,ymax,zmin,zmax,count,hCount,bCount]))
        
        fp.write(s+"\n")
        totalCount += count
        if count > 5:        
            print(s)
    setEncPts.Complete()
    fp.close()
    if brightSlices:
        clusterCSV.close()

    appendFilter.Update()

    cleanFilter = vtk.vtkCleanPolyData()
    cleanFilter.SetInputData(appendFilter.GetOutput())
    cleanFilter.Update()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(cleanFilter.GetOutput())
    mapper.Update()

    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.SetSize(800,800)
    renWin.AddRenderer(ren)
    ren.AddActor(actor)

    writer = vtk.vtkOBJExporter()
    writer.SetFilePrefix(isoDir+'iso_'+str(percent)+'_percent_filtered')
    writer.SetInput(renWin)
    writer.Write()
    
    fp = open(csvDir+'stars_in_regions_'+str(percent)+'.csv','w')
    for starName in stars:
        if starName in starRegion:
            fp.write(stars[starName]['line']+','+str(starRegion[starName])+"\n")
    fp.close()
