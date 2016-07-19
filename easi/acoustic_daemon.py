
import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A

__all__ = ["AcousticDaemon"]

class AcousticDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self,self.run,handler=self.handler,name="easi_daemon")

    def run(self):
        A = A.Acoustics()
        A.beginRun()#or wahtever it is

    def handler(self,fn):
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass

if __name__=="__main__":
    d = AcousticDaemon()
    # d.start()