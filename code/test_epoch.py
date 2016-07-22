import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np
import libEpoch
from urllib import urlopen as uo
from time import sleep, time

###Script Anne is using to learn data collection system

# def aread():
#     site = "http://localhost:9001/read/"
#     return uo(site).read().split("\n")[-3]
    

# def awrite(string):
#     site = "http://localhost:9001/writecf/"+string
#     uo(site).read()
#     sleep(.1)


# def processWaveform(stuff):
#     first = []
#     second = []
#     ps = stuff.split(")")
#     ps.pop(len(ps)-1)
#     for p in ps:
#         p = p.replace("(","")
#         d = p.split(",")
#         first.append(int(d[0],16)) 
#         second.append(int(d[1],16)) 
#     awrite("param_Range?")
#     sleep(.5)
#     rng = float(aread())
#     tim = np.linspace(0,rng,len(first))
#     return tim,first,second

# def battstat(stuff):
#     awrite("BATTSTAT?")
#     ans = str(self.getLast(ts=5))
#     # print ans
#     return ans

# def getLast(ts=300):
#     #takes last packet of information
#     global last
#     ticks = 0
#     while ticks < ts: 
#         ticks +=1
#         sleep(.05) #makes sure buffer has correct
#     last = aread(split="OK")
#     return last

# #where delay happen?

# awrite("param_WaveForm?")
# sleep(5)

# t,d1,d2 = processWaveform(aread())

# plt.plot(t,d1)
# plt.show()
# plt.clf()

# battery = battstat(aread())
# print (battery)

e = libEpoch.epoch(site=9001)
# print(e.battstat())
e.commanderPE()