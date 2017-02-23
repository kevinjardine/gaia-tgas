import numpy
from scipy.ndimage.filters import gaussian_filter as gf
from scipy.special import expit
import sys
import os
import matplotlib.pyplot as plt
import imageio.core

#config

rootDir = 'd:/projects/astronomy/tgas/'

#code

number_of_bins = 2
w = 800//number_of_bins

argv = sys.argv

hotSlices = False
brightSlices = False

if argv[1] == 'hot':
    sigma = 15/number_of_bins
    spread = 2000
    hotSlices = True
elif argv[1] == 'bright':
    sigma = 5/number_of_bins
    spread = 150
    brightSlices = True

tgas = {}

a = numpy.zeros(shape=(w*2,w*2,w*2))

fp = open(rootDir+'output/star_list/stars.csv','r')
line = fp.readline()
while len(line) != 0:
    bits = line.strip().split(',')
    if len(bits) > 1:
        name, colourIndex, xg, yg, zg, glon, glat, m, plx, pmra, pmdec, isHot, isBright = bits
        if (hotSlices and isHot == '1') or (brightSlices and isBright == '1'):
            x = int(round(float(xg)/number_of_bins))+w
            y = int(round(float(yg)/number_of_bins))+w
            z = int(round(float(zg)/number_of_bins))+w

            if x >= 0 and x < 2*w and y >= 0 and y < 2*w and z >= 0 and z < 2*w:
                a[x][y][z] += 1
    line = fp.readline()
fp.close()

gaussian = gf(a, sigma=sigma, truncate=3)
b = 2*(expit(spread*gaussian)-0.5)

if not os.path.isdir(rootDir+'output/slices'):
    os.mkdir(rootDir+'output/slices')

if hotSlices:
    sliceDir = rootDir+'output/slices/hot/'
elif brightSlices:
    sliceDir = rootDir+'output/slices/bright/'

if not os.path.isdir(sliceDir):
    os.mkdir(sliceDir)

if not os.path.isdir(sliceDir+'cm'):
    os.mkdir(sliceDir+'cm')

if not os.path.isdir(sliceDir+'16bit'):
    os.mkdir(sliceDir+'16bit')

count = 0
for tgasSlice in numpy.dsplit(b,2*w):
    print('slice', count)

    filename=sliceDir+'16bit/slice_'+str(count).zfill(4)+'.pgm'
    b2 = imageio.core.image_as_uint(tgasSlice, bitdepth=16)
    imageio.imwrite(filename,b2)

    filename=sliceDir+'cm/slice_'+str(count).zfill(4)+'.png'
    plt.imsave(filename,tgasSlice.squeeze(),cmap='inferno')

    count += 1