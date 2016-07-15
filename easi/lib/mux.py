
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
                debug('chan1=', chan , 'chan2=',chan2)
            else:
                u = self.url+"/write/%i,%i" % (int(chan),int(chan2))
                debug('chan1=', chan , 'chan2=',chan2)
            uo(u).read() #TODO: check the result
            self.on = [x for x in [chan,chan2] if x is not None and x is not 0]
            sleep(delay)
        except: #TODO: custom errors and handlers
            print("problem with mux")
            
