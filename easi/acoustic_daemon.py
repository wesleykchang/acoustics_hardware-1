
import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time

__all__ = ["AcousticDaemon"]

class AcousticDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self,self.run,name="easi_daemon")

    def run(self):
        while True:
            a = A.Acoustics(json_url= "http://feasible.pithy.io:4011/table_load",pulserurl="9003")
            a.beginRun(loop=False)
            self.stop()

    def handler(self,fn):
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass

class Tester(Daemon):
    def __init__(self):
        Daemon.__init__(self, run_fn=self.run_fn, name="poop")
    def run_fn(self):
        count = 0
        while True:
            open("tester", "a").write(str(count)+"\n")
            count += 1
            if count > 10:
                self.stop()
            time.sleep(1)

if __name__=="__main__":
    d = AcousticDaemon()
    d.start()
    # t = Tester()
    # t.start()