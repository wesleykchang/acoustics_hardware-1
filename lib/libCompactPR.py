##Author: 
##Date Started: 
##Notes: 

from urllib.request import urlopen as uo
from time import sleep
import pickle
import bisect
import matplotlib.pyplot as plt
import redpitaya as rp
import BKPrecision as bk

class CP():
    def __init__(self, site, rp_url=None, rp_port=5000, oscope=None):
        self.site = site
        self.lut = pickle.load(open('lib/CP_LUT','rb'))
        self.write("P0")
        if rp_url is None and oscope:
            self.rp = None
            self.oscope = bk.BKPrecision()
        else:
            self.rp = rp.RedPitaya(rp_url,port=rp_port)
            self.oscope = None

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
        if self.rp:
            self.rp.prime_trigger()
            g = int(row["gain(db)"])*10
        elif self.oscope:
            self.oscope.prime_trigger()
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
        self.write("P0")
        
        ##for now we don't care about Voltage or PRF
        # self.write("V%i" % int(row['voltage'])) 
        # self.write("P%i" % int(row['prf'])) #pulse repitition freq
        if self.rp:
            data = self.pitaya(float(row["delay(us)"]),float(row["time(us)"]))
        elif self.oscope:
            data = self.scope(float(row["delay(us)"]), float(row["time(us)"]), float(row['gain(db)']))
        else:
            data = self.pitaya(float(row["delay(us)"]),float(row["time(us)"]))
        return data

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
    print(cp.read())
    # data = cp.commander({"freq(mhz)":2.25,"filtermode":"33","mode(tr/pe)":"tr","gain(db)":10,"delay(us)":0,"time(us)":0})
    #print(data)
    #plt.plot(data[0],data[1])
    #plt.show()
