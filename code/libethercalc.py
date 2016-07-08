#whatever

from urllib import urlopen as uo
import os
import sys

def debug(s):
    print "[libethercalc] "+s

class Ether():
    def __init__(self,url):
        self.loc = os.path.dirname(os.path.realpath(__file__))
        self.url =url
        self.backup = self.loc +"/"+ self.url.split("/")[-1]
        self.using_backup = False
        self.rows=None
        self.refresh()
        debug("Using ethercalc sheet at: "+self.url)
        debug("Creating backups at: "+self.backup)
        #this is a good start. but clean it up and make the interface better than
        #calling ether.rows[2]['TR Gain (dB)']. That's ugly and annoying.
        #Leave self.rows in for compatibility/control, though

    def _pullIfAvailable(self):
        """Pull straight from ethercalc and save locally. If ethercalc dies,
           just continue to use the CSV and alert the user."""
        try:
            data = uo(self.url).read()
            if len(data) > 10: open(self.backup,"w").write(data)
            else: data = open(self.backup).read()
        except: #BZZT, get stored data
            try:
                data = open(self.backup,"r").read()
            except IOError:
                raise IOError("Can't read ethercalc and no backup exists!")
                    
            if not self.using_backup:
                print "Ethercalc read failed, reading from last backup:"
                print self.backup
                self.using_backup = True
        else:
            if self.using_backup:
                print "Ethercalc read successful. Going back to using it."
                self.using_backup = False
        return data

    def _parsecsv(self):
        splits = self._pullIfAvailable().split("\n")
        header = splits.pop(0).replace('\"','')
        cols = header.split(",")
        out = []
        for i in splits:
            p = i.split(",")
            if i.lower().find("skip") == -1:
                #the above condition will fail if a filename has "skip" in it
                out.append({})
                for j in range(len(p)):
                    out[-1][cols[j]] = p[j] 
        return out
    
    def refresh(self):
        self.rows = self._parsecsv()
    
    
if __name__=="__main__":
    e = Ether("http://localhost:9600/acoustic.csv")
    print e.rows[1]
    
    
