from pithy import *

from libacoustic import *

a = Acoustics(pulserurl="http://localhost:9003",muxurl="http://localhost:9001",pulser="siui")

while True:
    a.getSingleData({"Name":"20160322-NCA18650-relaytest-1","Run (y/n)":"y","Mode (tr/pe)":"tr","Channel":1,"Channel 2":7,"Delay (us)":0,"Freq (MHz)":2.5,"Time (us)":12,"Gain (dB)":95})
    
    time.sleep(10)
    
    a.getSingleData({"Name":"20160322-NCA18650-relaytest-2","Run (y/n)":"y","Mode (tr/pe)":"tr","Channel":2,"Channel 2":8,"Delay (us)":0,"Freq (MHz)":2.5,"Time (us)":12,"Gain (dB)":70})
    
    time.sleep(10)