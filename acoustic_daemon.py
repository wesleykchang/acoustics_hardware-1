import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import signal
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
from datetime import timedelta
sys.path.append('../EASI-analysis/analysis') #add saver functions to path
import filesystem
from uuid import getnode as get_mac
import logging
try:
    from os import scandir
except ImportError:
    from scandir import scandir
# import plotter #anne's plotting library

from flask_wtf import Form, validators
from wtforms import StringField, PasswordField
from flask import Flask, send_from_directory, request, Response, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user

import eventlet

eventlet.monkey_patch() #fuuuuuck

__all__ = ["AcousticDaemon"]
app = Flask(__name__)
app.config['DEBUG'] = False
app.config["SECRET_KEY"] = '\x94\xec:\xaf\xeb\xc7.\xd5\xe8J1\xbbX\xac\xa5\x92\xd3\xb0k9\x14\xc6\xe7c'
#app.config['HOST'] = "0.0.0.0"  #can change this to whatever

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "/login"
login_manager.session_protection = "strong"

socketio = SocketIO(app, binary=True)

class User(UserMixin):
    def __init__(self, username, password):
        self.id = username
        self.password = password

    def check_password(self,field_pword):
        return field_pword == self.password

    @classmethod
    def get(cls,id):
        user_database = {
                "Lab": User("Lab", "batteriesarelikerocks")}
        return user_database.get(id)

class LoginForm(Form):
    username = StringField('Username')
    password = PasswordField('Password')

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        user = User.get(self.username.data)
        if user is None:
            return False

        if not user.check_password(self.password.data):
            return False

        self.user = user
        return True


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
        self.saver = filesystem.Saver()

    def run(self):
        @login_manager.user_loader
        def load_user(user_id):
            return User.get(user_id)

        @app.route('/')
        @login_required
        def root():
            return send_from_directory('static','index.html')

        @app.route('/login', methods=['GET', 'POST'])
        def login():
            form = LoginForm()
            if form.validate_on_submit():
                login_user(form.user, remember=False)
                return redirect('/')
            return render_template('login.html', form=form)


        @app.route('/table_load')
        @login_required
        def table_load():
            table = json.loads(open("table_state.json").read())
            table["mac"] = str(get_mac())[-4:]
            return json.dumps(table)

        @app.route('/fonts/<path:filename>') #important for being able to load font files
        @login_required
        def custom_static(filename):
            return send_from_directory("fonts", filename)

        @app.route('/<month>/<day>/<year>/view')
        @login_required
        def view_table(month,day,year):
            return send_from_directory('static/tableviewer','index.html') #show logfile

        @app.route('/<month>/<day>/<year>/table_load')
        @login_required
        def log_load(month,day,year):
            startdate = year + '_' + month + '_' + day
            return open(os.path.join("../Data",startdate,"logfile.json")).read() #get data for a given log

        @app.route('/table_save', methods=['GET', 'POST'])
        @login_required
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
        @login_required
        def del_test(month,day,year):
            if request.method == 'POST':
                postdata = json.loads(request.get_data().decode('utf-8'))
                startdate = year + '_' + month + '_' + day
                path = os.path.join("../Data",startdate,"logfile.json")
                tests_run = json.load(open(path))['data']
                for key in tests_run:
                    entry = tests_run[key]
                    if key == postdata['rowid']:
                        if not os.path.exists("../Data/Trash"):
                            os.mkdir("../Data/Trash")
                        shutil.move(os.path.join("../Data",startdate,"TestID_" + entry['testid']),("../Data/Trash"))
                        self.saver.writeLog(entry,trash=True) #writes to the trash log
                        del tests_run[key]
                        json.dump({'data':tests_run}, open(path,'w'))
                        return "ok"

        @app.route('/<month>/<day>/<year>/viewfigs')
        @login_required
        def viewfigs(month,day,year):
            return send_from_directory('static/figviewer','index.html')

        @app.route('/<month>/<day>/<year>/<testid>/makefigs')
        @login_required
        def makefig(month,day,year,testid):
            start_date = year + '_' + month + '_' + day
            files = os.listdir(os.path.join('../Data',start_date,testid))
            files.remove('current.json')
            files = sorted(files)

            index = int(request.args.get('index', ''))
            data = json.load(open(os.path.join('../Data',start_date,testid,files[index])))
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
            plt.close(fig)
            return json.dumps(out)

        @socketio.on('test')
        def handle_test(data):
            socketio.emit('update', data) #tell the JS to update.

        @socketio.on('highlight')
        def active_row(rowid):
            socketio.emit('active', rowid)
                        
        while True:
            # socketio.run(app,host="0.0.0.0",port=5000)  
            socketio.run(app,port=self.port)  

    def loadTools(self):
        pass

class DBDaemon(Daemon):
    def __init__(self,every_n_min=None):
        Daemon.__init__(self,self.run,name="db_daemon")
        # self.loader = filesystem.Loader()
        # self.datapath = self.loader.path
        self.datapath = "../Data"
        self.n_min = every_n_min
        #logging stuffs

        signal.signal(signal.SIGINT,  self.cleanobs)
        signal.signal(signal.SIGQUIT, self.cleanobs)
        signal.signal(signal.SIGTERM, self.cleanobs)


    def modified_since(self,cutoff,path):
        files = set([])
        for f in scandir(path):
            mtime = f.stat().st_mtime
            if mtime > cutoff:
                if f.is_dir():
                    for i in self.modified_since(cutoff,f.path):
                        files.add(i)
                else:
                    # print("YES! {} ".format(mtime))
                    files.add(f.path)
            else:
                pass
        return files

    def check_all_dates(self):
        cutoff = time.time() - (self.n_min*60) #defaults to push files at same interval
        all_mod_files = []
        for date_folder in os.listdir(self.datapath):
            mod_files = self.modified_since(cutoff,os.path.join(self.datapath,date_folder))
            all_mod_files.append(mod_files)
        return all_mod_files


    def push_files(self):
        mod_files = self.modified_since()

    def cleanobs(self,*args):
        print("add push all data here")
        pass

    def run(self):
        while True:
            time.sleep(6)
            print(self.check_all_dates())
        #stuff to do.

    def handler(self,fn): #need to reimplement this. right now it's stdin and stdout.
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass



if __name__=="__main__":
    pulserurl = 9003
    muxurl = 9002
    host = "0.0.0.0"
    port = 6054
    for i in sys.argv:
        if i.find("=") > 0: 
            print(i)
            exec(i)
            
    d = UIDaemon(port,host)
    d.start()
    time.sleep(1)

    dbd = DBDaemon(.1)
    dbd.start()

    ad = AcousticDaemon(uiurl=port,muxurl=muxurl,muxtype="cytec",pulserurl=pulserurl)
    ad.start()
