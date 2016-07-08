
from daemon import Daemon
import lib.libacoustic as A

__all__ = ["AcousticDaemon"]

class AcousticDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self,self.run,handler=self.handler)

    def run(self):
        A.beginRun()#or wahtever it is

    def handler(self,fn):
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass
