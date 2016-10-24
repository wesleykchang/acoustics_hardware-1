
from urllib.request import urlopen as uo
from time import sleep

__all__ = ["Mux"]

class Mux():
    def __init__(self,url,fake=False):
        self.url = url
        self.on = []
        self.fake = fake

    def debug(self,msg):
        if __debug__:
            print(msg)

    def get(self):
        return self.on

    def switch(self,chan,chan2=None,delay=0.5):
        try:
            if chan2 is None:
                u = self.url+"/write/%i" % int(chan)
                #self.debug('chan1='+str(chan)+', chan2='+str(chan2))
            else:
                u = self.url+"/write/%i,%i" % (int(chan),int(chan2))
                #self.debug('chan1='+str(chan)+', chan2='+str(chan2))
            uo(u).read() #TODO: check the result
            self.on = [x for x in [chan,chan2] if x is not None and x is not 0]
            sleep(delay)
        except Exception as E: #TODO: custom errors and handlers
            raise(E)
            print("problem with mux")
            
