##Author: 
##Date Started: 
##Notes: 

from urllib.request import urlopen as uo
from time import sleep, time
import pickle
import bisect
import redpitaya as rp
import BKPrecision as bk
import libPicoscope

class CP():
    def __init__(self, site, rp_url="169.254.1.10", rp_port=5000, voltage=200, scope='picoscope'):
        self.voltage = voltage
        self.site = site
        self.lut = pickle.load(open('lib/CP_LUT','rb'))
        self.write("P0")
        self.scope = scope
        
        if self.scope == 'picoscope':
            self.pss = libPicoscope.Picoscope()
            self.rp = None
            self.oscope = None
        elif self.scope == 'bkprecision':
            self.oscope = bk.BKPrecision()
            self.rp = None
            self.pss = None
        elif self.scope == 'redpitaya':
            self.rp = rp.RedPitaya(rp_url,port=rp_port)
            self.oscope = None
            self.pss = None

    def write(self,s):
        out = uo(self.site+"/writecf/%s"%s).read()
        sleep(.05)
        return out

    def read(self):
        return uo(self.site+"/read/").read().decode('utf-8').split("\r")[-2]

    def getLast(self,ts=300):
        global last
        ticks = 0
        while ticks < ts: 
            ticks +=1
            sleep(.05)
        last = self.aread(split="OK")
        return last

    def convertFreq(self, freq):
        """Takes a frequency(in MHz) and converts it to a CP setting"""
        pw = int(1/(float(freq)*1e-3))
        # print(pw)
        if pw <= 484:
            wide = "X0"
            val = self.returnNearest(list(sorted(self.lut.values())),pw)
            CPval = "W%i" % val
        else:
            wide = "X1"
            keys = (list(self.lut.keys())) #keys are ordered in incremental fashion val = self.returnNearest(keys,pw)
            val = self.returnNearest(keys,pw)
            CPval = "W%i" % self.lut[val]
        return [CPval,wide]

    def convertFilt(self,filtmode):
        """Takes a filtermode with the 1st digit as the hp filter and the 2nd digit as the lp filter"""
        hpf = "H0"
        lpf = "L0"
        settings = list(filtmode)
        if len(settings) == 2:
            hpf = "H%i" % int(settings[0])
            lpf = "L%i" % int(settings[1])
        return [hpf,lpf]

    def returnNearest(self,l,pw):
        """Takes an int and a list of ints, and finds the closest list value to the int"""
        ind = (bisect.bisect_left(l, pw))
        if pw >= 2285:
            val = 2285
            print ("Frequency is lower than lowest possible. setting frequency to .437 MHz")
        else:
            val = (min([l[ind],l[ind-1]], key=lambda k: abs(k-pw)))       
        return val

    def commander(self,row):
        """Takes a row of settings and sets params on CompactPulser"""

        #anne's note to self: add some defaults
        g = row["gain(db)"]

        if self.rp:
            try:
                g = int(g)*10
            except ValueError:
                print('invalid gain level')
                return
            self.rp.prime_trigger()
            
        elif self.oscope:
            try:
                maxV = float(g)
                self.oscope.set_maxV(maxV)
            except ValueError:
                print('invalid gain level')
                return
            self.oscope.prime_trigger()
            g = 20
        elif self.pss:
            #initiate ps connection, this is a product of having a daemonized process
            self.pss.connect()
            try:
                maxV = float(g)
                self.pss.set_maxV(maxV)
            except ValueError:
                if g == 'auto':
                    self.write('P100')
                    self.pss.auto_range(float(row["delay(us)"]),float(row["time(us)"]))
                    self.write('P0')
                else:
                    raise ValueError('invalid gain level')
                
            self.pss.prime_trigger(float(row["delay(us)"]),float(row["time(us)"]))
            row['gain(db)'] = self.pss.get_maxV() #get the actual clipping voltage

        g = 20
        [pwidth,widemode] = self.convertFreq(row["freq(mhz)"])
        [hpf, lpf] = self.convertFilt(row["filtermode"])
        settings = {"tr" : "M1", "pe" : "M0"}

        self.write(settings[row['mode(tr/pe)']])
        self.write(hpf)
        self.write(lpf)
        self.write("G%i" % g) #gain is measured in 10th of dB 34.9 dB =349
        self.write(widemode)
        self.write(pwidth)
        self.write("V%i" % self.voltage)
        
        if self.rp:
            self.write('P0')
            data = self.pitaya(float(row["delay(us)"]),float(row["time(us)"]))
        elif self.oscope:
            self.write('P0')
            data = self.scope(float(row["delay(us)"]), float(row["time(us)"]), float(row['gain(db)']))
        elif self.pss:
            self.write('P100')
            self.pss.wait_ready()
            self.write('P0')
            data = self.pico()
            
        return data

    def pico(self):
        return self.pss.get_waveform(wait_for_trigger=False)
    
    def scope(self, delay, duration, volt_limit):
        return self.oscope.get_waveform(delay=delay, duration=duration, volt_limit=volt_limit)
        
    def pitaya(self, delay, time):
        """Get waveform from red pitaya"""
        if self.rp is None:
            return {} #should this raise an exception?
        else:
            data = self.rp.get_waveform(delay=delay,time=time)
        return data

if __name__ == "__main__":

    cp = CP("http://localhost:9003",rp_url="169.254.134.177")
    print(cp.write("T?"))
    print(cp.write("V"))
    # print(cp.read())
    # data = cp.commander({"freq(mhz)":2.25,"filtermode":"33","mode(tr/pe)":"tr","gain(db)":10,"delay(us)":0,"time(us)":0})
    #print(data)
    #plt.plot(data[0],data[1])
    #plt.show()
