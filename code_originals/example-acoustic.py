from pithy import *
from libacoustic import *

a = Acoustics(etherurl="http://localhost:9600/acoustic.csv",muxurl="http://localhost:9002/",pulser="siui",pulserurl="http://localhost:9003")

print a.ether.rows

#print a.ether.rows[0]
print a.getSingleData(a.ether.rows[0])

#a.beginRun()