##Author: 
##Date Started: 
##Notes: 

from urllib.request import urlopen as uo
from time import sleep
import pickle
import bisect

class CP():
    def __init__(self,site):
        self.site = site

    def write(self,s):
        out = uo(self.site+"/writecf/%s"%s).read()
        sleep(.05)
        return out

    def read(self):
        return uo(self.site+"/read/").read().split("\r")[-2]

    def getLast(self,ts=300):
        global last
        ticks = 0
        while ticks < ts: 
            ticks +=1
            sleep(.05)
        last = self.aread(split="OK")
        return last

    def convertFreq(self, freq):
        pw = int(1/(freq*1e-3))
        print(pw)
        lut = pickle.load(open('CP_LUT','rb'))
        if pw <= 484:
            wide = False
            print(sorted(lut.values()))
            val = self.returnNearest(list(sorted(lut.values())),pw)
            CPval = val
        else:
            wide = True
            keys = (list(lut.keys())) #keys are ordered in incremental fashion
            val = self.returnNearest(keys,pw)
            CPval = lut[val]
        return [CPval,wide]

    def returnNearest(self,l,pw):
        ind = (bisect.bisect_left(l, pw))
        try:
            val = (min([l[ind],l[ind-1]], key=lambda k: abs(k-pw)))
        except IndexError:
            val = 2285
            print ("Frequency is lower than lowest possible. setting frequency to .437 MHz")
        return val


    def commander(self,row):
        settings = {"tr" : "M1", "pe" : "M0"}

        self.write("G%i" % int(row["gain"]*10)) #gain is measured in 10th of dB 34.9 dB =349
        self.write(settings[row['mode(tr/pe)']])
        self.write("L%i" % int(row['lpf']))
        self.write("H%i" % int(row['hpf']))
        self.write("V%i" % int(row['voltage']))
        self.write("P%i" % int(row['prf'])) #pulse repitition freq
        self.write("W%i" % int(row['pwidth'])) #wide pulse mode will need a LUT

        data = self.pitaya(delay,range)
        return data

    def pitaya(delay,range):
        return data
        pass

if __name__ == "__main__":

    test = CP("yolo")
    print(test.convertFreq(.5))

    # #Write a few settings
    # #Damping
    # print "Adjusting some settings"
    # c.write("D5")
    # #Voltage
    # c.write("V100")
    # #Transducer mode - 1 = TR, 2 = PE
    # c.write("M0")
    # #Gain GXYZ = XY.Z dB
    # c.write("G080")
    # c.write("H0")
    # c.write("L7")
    # c.write("P10")
    # c.write("Q500")
    # c.write("W200")



    # #Show All Settings
    # print "Showing settings:"
    # for i in l: 
    #     c.write("%s?"%i)
    #     print c.read()