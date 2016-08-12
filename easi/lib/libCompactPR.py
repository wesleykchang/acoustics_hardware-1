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




if __name__ == "__main__":

    site = "http://25.68.137.216:9000"
    c = CP(site)
    l = "DGHLMPQRSTVW"

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