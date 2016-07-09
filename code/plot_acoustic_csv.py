##Author: Dan Steingart
##Date Started: 7/1/2016
##Notes: Simple Plot of Acoustic Data

from pithy import *
from os.path import getmtime,getsize
fils = glob("/var/drops/files/acoustic_csvs/*.csv")

fils = sorted(fils,key = lambda k: getsize(k))
print len(fils)

f = fils[-1]
data = genfromtxt(f,delimiter=",",invalid_raise=False)
data = data.T
lt = data[0][-1]
imshow(data[2:][:],aspect="auto")

showme()
clf()
