
import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import argparse
from http.server import SimpleHTTPRequestHandler
import socketserver


__all__ = ["AcousticDaemon"]

class AcousticDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self,self.run,name="easi_daemon")

    def run(self):
        while True:
            a = A.Acoustics(json_url= "http://feasible.pithy.io:4011/table_load",pulserurl="9003")
            a.beginRun()

    def handler(self,fn): #need to reimplement this. right now it's stdin and stdout.
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass

class WebDaemon(Daemon):
    def __init__(self,port):
        Daemon.__init__(self,self.run,name="web_daemon")
        self.port= port

    def start(self):
        Handler = SimpleHTTPRequestHandler
        self.httpd = socketserver.TCPServer(("", self.port), Handler)
        print (time.asctime(), "Server Starts - %s:%s" % ("localhost", self.port))
        return Daemon.start(self)

    def stop(self):
        self.httpd.server_close()
        print (time.asctime(), "Server Stops - %s:%s" % ("localhost", self.port))
        return Daemon.stop(self)

    def run(self):
        self.httpd.serve_forever()

    def loadTools(self):
        pass

if __name__=="__main__":
    d = WebDaemon(port=8001)
    d.start()

    # ad = AcousticDaemon()
    # ad.start()




    #argparser from command line. to finish later.
    # parser = argparse.ArgumentParser(description="Starts/Stops the acoustic daemon")
    # parser.add_argument('start', help="Starts daemon")
    # parser.add_argument('stop', help="Stops daemon")
    # args = parser.parse_args()

    # if args.start:
    #     d.start()

    # if args.stop:
    #     d.stop()