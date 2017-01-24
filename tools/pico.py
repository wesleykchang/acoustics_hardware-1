import sys
import time
from pylab import *
#sys.path.append('../EASI-analysis/analysis') 
sys.path.append('../lib') 

import redpitaya
import cytec

def avg_wave(waves):
    xs = []
    ys = []
    for i in range(len(waves[0][0])):
        totx = []
        toty = []
        for j in range(len(waves)):
            totx.append(waves[j][0][i])
            toty.append(waves[j][1][i])
        xs.append(sum(totx)/float(len(waves)))
        ys.append(sum(toty)/float(len(waves)))
    return [xs,ys]
        

rp = redpitaya.RedPitaya("169.254.1.10")
mux = cytec.Mux("http://localhost:9002")

mux.latch([(0,7),(6,7)])
time.sleep(0.1)
rp.prime_trigger()
wave = rp.get_waveform(delay=2,time=20)
#open("pouch.dat","w").write(str(wave)+"\n")
subplot(211)
plot(wave[0],wave[1])

mux.latch([(0,6),(6,6)])
time.sleep(0.1)
waves = []
subplot(212)
for i in range(10):
    rp.prime_trigger()
    wave = rp.get_waveform(delay=2,time=20)
    waves.append(wave)
    plot(wave[0],wave[1])
#subplot(212)
#plot(wave[0],wave[1])

subplot(211)
tit = "30 dB 300V scaled"
xlabel("ToF")
ylabel("Amplitude")
title(tit)
savefig("".join([x for x in tit if x!=" "])+".png")
show()

