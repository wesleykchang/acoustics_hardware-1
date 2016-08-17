##Author: 
##Date Started: 
##Notes: 

from urllib import urlopen as uo
from time import sleep


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
    

    def commander(self,row):
        settings = {"tr" : "M1", "pe" : "M0"}

        self.write("G%i" % int(row["gain"]*10)) #gain is measured in 10th of dB 34.9 dB =349
        self.write(settings[row['mode(tr/pe)']])
        self.write("L%i" % int(row['lpf']))
        self.write("H%i" % int(row['hpf']))
        self.write("V%i" % int(row['voltage']))
        self.write("P%i" % int(row['prf'])) #pulse repitition freq
        self.write("W%i" % int(row['pwidth'])) #wide pulse mode will need a LUT

        data = self.pitaya()
        return data

    def pitaya():
        pass

if __name__ == "__main__":

    #Write a few settings
    #Damping
    print "Adjusting some settings"
    c.write("D5")
    #Voltage
    c.write("V100")
    #Transducer mode - 1 = TR, 2 = PE
    c.write("M0")
    #Gain GXYZ = XY.Z dB
    c.write("G080")
    c.write("H0")
    c.write("L7")
    c.write("P10")
    c.write("Q500")
    c.write("W200")



    #Show All Settings
    print "Showing settings:"
    for i in l: 
        c.write("%s?"%i)
        print c.read()