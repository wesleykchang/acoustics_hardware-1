
import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import argparse
from http.server import SimpleHTTPRequestHandler
import socketserver
import json

from flask import Flask, send_from_directory, request

__all__ = ["AcousticDaemon"]
app = Flask(__name__)

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


class UIDaemon(Daemon):
    def __init__(self):
        Daemon.__init__(self,self.run,name="ui_daemon")

    def run(self):
        @app.route('/')
        def root():
            return send_from_directory('static','index.html')

        @app.route('/table_load')
        def table_load():
            return open("table_state.json").read()


        @app.route('/table_save', methods=['GET', 'POST'])
        def table_save():
            # if request.method == 'POST':
                out = {}
                try:
                    test = request.get_data().decode('utf-8')
                    open("table_state.json",'w').write(test)
                    open("table_state_%i.json" % int(time.time()),'w').write(test)
                    out = json.loads(test)
                    out['status'] = 'success IS THE BEST'
                except Exception as E: 
                    out['status'] = str(E)
                return json.dumps(out)
        while True:        
            app.run() #if you call this with debug=true, daemon will init twice. weird.

    def loadTools(self):
        pass


if __name__=="__main__":
    d = UIDaemon()
    d.start()

    # ad = AcousticDaemon()
    # ad.start()