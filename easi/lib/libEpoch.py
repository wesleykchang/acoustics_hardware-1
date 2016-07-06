from urllib.request import urlopen as uo
from io import StringIO
from time import sleep
from numpy import *

import fakeEpoch

class epoch():
    def __init__(self,site,fake=False):
        self.site = site
        self.delay = .25
        self.fake = fake
        self.fake_buffer = []
        
    def awrite(self,val,verbose=False):
        if verbose: print("Asking for",val,":")
        if self.fake:
            self.fake_buffer.append(val)
        else:
            uo(self.site+"/writecf/"+str(val)).read()
        sleep(self.delay)
     
    def aread(self,split=None):
        if fake:
            get = ""
            for i in self.fake_buffer:
                if i=="process_WaveForm?":
                    get.append(get+"OK") #add real (fake) data
                else:
                    get.append(fakeEpoch.param(0))
        else:
            get = uo(self.site+"/read/").read()
            if split != None:
                for i in range(1,6):
                    out = get.split("OK")[-i]
                    if out=="\r\n": continue
                    else: break
                # print(out)
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
    
    def commander(self,isTR='tr',gain=25,tus_scale=40,freq=2.25,delay=0,filt=0):
        if isTR=='tr':
            return self.commanderTR(gain,tus_scale,freq,delay,filt)
        elif isTR=='pe':
            return self.commanderPE(gain,tus_scale,freq,delay,filt)
        else:
            print('what mode you in?')
    
    def commanderPE(self,gain=25,tus_scale=40,freq=2.25,delay=0,filt=3):
        self.awrite("param_Freq=%f" % freq,verbose=False)
        self.awrite("param_Range=%f" % tus_scale,verbose=False)
        self.awrite("param_BaseGain=%f" % gain,verbose=False)
        self.awrite("param_FilterStandard=%i" % filt,verbose=False)
        self.awrite("param_TransmissionMode=0",verbose=False)
        self.awrite("param_Delay=%f" % delay,verbose=False)
        self.awrite("param_WaveForm?",verbose=False)
        raw = self.getLast()
        # open("epoch-emergency-log","a").write(str(freq)+","+str(tus_scale)+","+str(gain)+","+str(delay))
        # open("epoch-emergency-log","a").write(raw)
        data = self.processWaveform(raw)
        return data

    def commanderTR(self,gain=25,tus_scale=40,freq=2.25,delay=0,filt=3):
        self.awrite("param_Freq=%f" % freq,verbose=False)
        self.awrite("param_Range=%f" % tus_scale,verbose=False)
        self.awrite("param_BaseGain=%f" % gain,verbose=False)
        self.awrite("param_FilterStandard=%i" % filt,verbose=False)
        self.awrite("param_TransmissionMode=2",verbose=False)
        self.awrite("param_Delay=%f" % delay,verbose=False)
        self.awrite("param_WaveForm?",verbose=False)
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


