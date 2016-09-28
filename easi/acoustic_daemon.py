import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import argparse
from http.server import SimpleHTTPRequestHandler
import socketserver
import json
import utils
import os,shutil
from flask_socketio import SocketIO, send, emit
import matplotlib
from matplotlib import pyplot as plt
import mpld3
import plotter #anne's plotting library

from flask import Flask, send_from_directory, request

import eventlet

eventlet.monkey_patch() #fuuuuuck

__all__ = ["AcousticDaemon"]
app = Flask(__name__)
app.config['DEBUG'] = False
#app.config['HOST'] = "0.0.0.0"  #can change this to whatever
socketio = SocketIO(app, binary=True)


class AcousticDaemon(Daemon):
    def __init__(self,uiurl=5000,muxurl=9002,muxtype="cytec",pulserurl=9003, pulser="compact"):
        Daemon.__init__(self,self.run,name="easi_daemon")
        self.uiurl =  utils.parse_URL(uiurl)
        self.muxurl =  utils.parse_URL(muxurl)
        self.muxtype = muxtype
        self.pulserurl =  utils.parse_URL(pulserurl)
        self.acous = A.Acoustics(pulserurl=self.pulserurl,muxurl=self.muxurl,muxtype=muxtype)

    def run(self):
        while True:
            self.acous.beginRun()

    def handler(self,fn): #need to reimplement this. right now it's stdin and stdout.
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass


class UIDaemon(Daemon):
    """Responsible for hosting the web interface."""
    def __init__(self,port=5000,host=None):
        Daemon.__init__(self,self.run,name="ui_daemon")
        self.port = port
        self.host = host

    def run(self):
        def writeLog(row):
            """Attempts to open a log file and add the row to it. If there is no logfile, creates one."""
            logname = os.path.join("Data/Trash","logfile.json") #path to logfile:
            if os.path.exists(logname):
                info = json.load(open(logname))
            else:
                info = {'data' : []}  
            info['data'].append(row) #append to the list of dicts
            json.dump(info, open(logname, 'w'))

        def parse_month(month,day,year):
            months =   {'01' : 'Jan', '02' : 'Feb',
                        '03' : 'Mar', '04' : 'Apr',
                        '05' : 'May', '06' : 'Jun',
                        '07' : 'Jul', '08' : 'Aug',
                        '09' : 'Sep', '10' : 'Oct',
                        '11' : 'Nov', '12' : 'Dec'}
            startdate = months[month] + '_' + day + '_' + year
            return startdate


        @app.route('/')
        def root():
            return send_from_directory('static','index.html')

        @app.route('/table_load')
        def table_load():
            return open("table_state.json").read()

        @app.route('/fonts/<path:filename>') #important for being able to load font files
        def custom_static(filename):
            return send_from_directory("fonts", filename)

        @app.route('/<month>/<day>/<year>/view')
        def view_table(month,day,year):
            return send_from_directory('static/tableviewer','index.html') #show logfile

        @app.route('/<month>/<day>/<year>/table_load')
        def log_load(month,day,year):
            startdate = parse_month(month,day,year)
            return open(os.path.join("Data",startdate,"logfile.json")).read() #get data for a given log

        @app.route('/table_save', methods=['GET', 'POST'])
        def table_save():
            # if request.method == 'POST':
                out = {}
                try:
                    test = request.get_data().decode('utf-8')
                    open("table_state.json",'w').write(test)
                    # open("table_state_%i.json" % int(time.time()),'w').write(test)
                    out = json.loads(test)
                    out['status'] = 'success!'
                except Exception as E: 
                    out['status'] = str(E)
                return json.dumps(out)

        @app.route('/<month>/<day>/<year>/del_test', methods=['GET', 'POST'])
        def del_test(month,day,year):
            if request.method == 'POST':
                postdata = json.loads(request.get_data().decode('utf-8'))
                startdate = parse_month(month,day,year)
                path = os.path.join("Data",startdate,"logfile.json")
                tests_run = json.load(open(path))['data']
                for entry in tests_run:
                    if entry['testid'] == postdata['rowid']:
                        if not os.path.exists("Data/Trash"):
                            os.mkdir("Data/Trash")
                        shutil.move(os.path.join("Data",startdate,"TestID_" + postdata['rowid']),("Data/Trash"))
                        writeLog(entry)
                        tests_run.remove(entry)
                json.dump({'data':tests_run}, open(path,'w'))
                return "ok"

        @app.route('/<month>/<day>/<year>/viewfigs')
        def viewfigs(month,day,year):
            return send_from_directory('static/figviewer','index.html')

        @app.route('/<month>/<day>/<year>/<testid>/makefigs')
        def makefig(month,day,year,testid):
            start_date = parse_month(month,day,year)
            files = os.listdir(os.path.join('Data',start_date,testid))
            files.remove('current.json')
            files = sorted(files)

            index = int(request.args.get('index', ''))
            data = json.load(open(os.path.join('Data',start_date,testid,files[index])))
            xs = [x*0.008 for x in range(len(data['amp']))]
            fig = plt.figure()
            plt.plot(xs,data['amp'])
            plt.ylabel('Amplitude')
            plt.xlabel('Time of Flight (us)')
            plt.title(files[index].rstrip('.json'))
            wave = mpld3.fig_to_dict(fig)


            out = {}
            out['fig1'] = wave
            out['lenfigs'] = [str(index), str(len(files)-1)]
            return json.dumps(out)

        @app.route('/fsweep')
        def sweep_fs():
            return send_from_directory('static','sweepdex.html')

        @socketio.on('test')
        def handle_test(data):
            socketio.emit('update', data) #tell the JS to update.

        @socketio.on('highlight')
        def active_row(rowid):
            socketio.emit('active', rowid)
                        
        while True:
            # socketio.run(app,host="0.0.0.0",port=5000)  
            socketio.run(app,host="0.0.0.0",port=5000)  

    def loadTools(self):
        pass


if __name__=="__main__":
    pulserurl = 9003
    muxurl = 9000
    host = "0.0.0.0"
    port = 5000
    for i in sys.argv:
        if i.find("=") > 0: 
            print(i)
            exec(i)
            
    d = UIDaemon(port,host)
    d.start()
    time.sleep(1)
    # ad = AcousticDaemon(uiurl=port,muxurl=None,muxtype="old",pulserurl=pulserurl)
    # ad.start()
