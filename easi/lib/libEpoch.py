from urllib.request import urlopen as uo
from io import StringIO
from time import sleep
from numpy import *

import fakeEpoch

class Epoch():
    def __init__(self,site, fake=False):
        self.site = site #localhost port for epoch. string.
        self.delay = .25
        self.fake = fake
        self.fake_buffer = []
        
    def awrite(self,val):
        if verbose: print ("Asking for",val,":")
        uo(self.site+"/writecf/"+str(val)).read()
        sleep(self.delay)
     
    def aread(self,split=None):
        get = uo(self.site+"/read/").read().decode('utf-8') #need to decode for python3
        if split != None:
            for i in range(1,6):
                out = get.split("OK")[-i]
                if out=="\r\n": continue
                else: break
            # print out
            return out.strip()
            #return get.split("OK")[-2].strip()
        return get

    def getLast(self,ts=300):
        global last
        ticks = 0
        while ticks < ts: 
            ticks +=1
            sleep(.05)
        last = self.aread(split="OK")
        return last
    
    def processWaveform(self,stuff):
        first = []
        second = []
        ps = stuff.split(")")
        ps.pop(len(ps)-1)
        for p in ps:
            p = p.replace("(","")
            d = p.split(",")
            first.append(int(d[0],16)) 
            second.append(int(d[1],16)) 
        
        #for outputting the right ToF values
        self.awrite("param_Delay?")
        sleep(self.delay)
        dely = float(self.getLast(ts=10))
        self.awrite("param_Range?")
        sleep(self.delay)
        rng = float(self.getLast(ts=10))
        tim = linspace(dely,rng+dely,len(first))
        rtime = [round(x,3) for x in list(tim)]
        return rtime,first,second
    
    def commander(self,row):
        defaults ={'isTR':'tr',"gain" : "25","tus_scale" :"40","freq":"2.25","delay":"0","filt":"3"}
        settings = {"tr" : "param_TransmissionMode=2", "pe" : "param_TransmissionMode=0"}

        try:
            isTR=row['mode(tr/pe)'].lower(),
            gain=float(row['gain(db)']),
            tus_scale=int(row['time(us)']),
            freq=float(row['freq(mhz)']),
            delay=float(row['delay(us)']),
            filt=float(row['filtermode'])
        except KeyError as e:
            row[e.args[0]]=defaults[e.args[0]] #sets to a default if no value is found for a row.


        self.awrite("param_Freq=%f" % freq)
        self.awrite("param_Range=%f" % tus_scale)
        self.awrite("param_BaseGain=%f" % gain)
        self.awrite("param_FilterStandard=%i" % filt)
        self.awrite("param_Delay=%f" % delay)
        self.awrite(settings[row['mode(tr/pe)']]) #sets the mode
        self.awrite("param_WaveForm?")
    
        raw = self.getLast()
        # open("epoch-emergency-log","a").write(str(freq)+","+str(tus_scale)+","+str(gain)+","+str(delay))
        # open("epoch-emergency-log","a").write(raw)
        data = self.processWaveform(raw)
        return data

    def battstat(self):
        self.awrite("BATTSTAT?", verbose = False)
        ans = str(self.getLast(ts=5))
        # print(ans)
        return ans


