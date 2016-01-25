from urllib import urlopen as uo
from StringIO import StringIO
from time import sleep
from numpy import *

class epoch():
    def __init__(self,site):
        self.site = site
        self.delay = .25
        
    def awrite(self,val,verbose=False):
        if verbose: print "Asking for",val,":"
        uo(self.site+"/writecf/"+str(val)).read()
        sleep(self.delay)
     
    def aread(self,split=None):
        get = uo(self.site+"/read/").read()
        if split != None:
            #if it needs more than this range, there's probably an issue
            #let it error
            
            print get
            
            for i in range(1,6):
                out = get.split("OK")[-i]
                if out=="\r\n": continue
                else: break
            print out
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
        self.awrite("param_Range?")
        sleep(self.delay)
        rng = float(self.getLast(ts=10)) #was 5
        tim = linspace(0,rng,len(first))
        return tim,first,second
    
    def commander(self,isTR=False,gain=25,tus_scale=40,freq=2.25,delay=0):
        if isTR:
            return self.commanderTR(gain,tus_scale,freq,delay)
        else:
            return self.commanderPE(gain,tus_scale,freq,delay)
    
    def commanderPE(self,gain=25,tus_scale=40,freq=2.25,delay=0):
        self.awrite("param_Freq=%f" % freq,verbose=False)
        self.awrite("param_Range=%f" % tus_scale,verbose=False)
        self.awrite("param_BaseGain=%f" % gain,verbose=False)
        self.awrite("param_TransmissionMode=0",verbose=False)
        self.awrite("param_Delay=%f" % delay,verbose=False)
        self.awrite("param_WaveForm?",verbose=False)
        raw = self.getLast()
        open("epoch-emergency-log","a").write(str(freq)+","+str(tus_scale)+","+str(gain)+","+str(delay))
        open("epoch-emergency-log","a").write(raw)
        data = self.processWaveform(raw)
        return data

    def commanderTR(self,gain=25,tus_scale=40,freq=2.25,delay=0):
        self.awrite("param_Freq=%f" % freq,verbose=False)
        self.awrite("param_Range=%f" % tus_scale,verbose=False)
        self.awrite("param_BaseGain=%f" % gain,verbose=False)
        self.awrite("param_TransmissionMode=2",verbose=False)
        self.awrite("param_Delay=%f" % delay,verbose=False)
        self.awrite("param_WaveForm?",verbose=False)
        raw = self.getLast()
        open("epoch-emergency-log","a").write(str(freq)+","+str(tus_scale)+","+str(gain)+","+str(delay))
        open("epoch-emergency-log","a").write(raw)
        data = self.processWaveform(raw)
        return data
    
    def battstat(self):
        self.awrite("BATTSTAT?", verbose = False)
        ans = str(self.getLast(ts=5))
        # print ans
        return ans
