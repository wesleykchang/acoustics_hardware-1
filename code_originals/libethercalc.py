#whatever

from urllib import urlopen as uo

class Ether():
    def __init__(self,url):
        self.url =url
        self.rows=None
        self.refresh()
        #this is a good start. but clean it up and make the interface better than
        #calling ether.rows[2]['TR Gain (dB)']. That's ugly and annoying.
        #Leave self.rows in for compatibility/control, though

    def _parsecsv(self):
        splits = uo(self.url).read().split("\n")
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
    
    
