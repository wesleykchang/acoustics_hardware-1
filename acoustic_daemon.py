import sys
sys.path.append('lib') #tells python where to look for packages
from daemon import Daemon
import libacoustic as A
import time
import signal
import operator
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
import datetime
sys.path.append('../EASI-analysis/analysis') #add saver functions to path
import filesystem
import database
import fcntl, socket, struct
import logging
import collections
try:
    from os import scandir
except ImportError:
    from scandir import scandir

from flask_wtf import Form, validators
from wtforms import StringField, PasswordField
from flask import Flask, send_from_directory, request, Response, render_template, redirect, url_for
from flask_login import LoginManager, UserMixin, login_required, login_user

import eventlet
import re #regex library
import data

from slack import SlackPoster

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
    """Class to keep track of users and authenticate when accessing daemon"""
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


class WatcherDaemon(Daemon):
    def __init__(self,
                 update_intervals={'easi_daemon': 10, 'db_daemon': 24.0*60.0}):
    
        Daemon.__init__(self, self.run, name="watcher_daemon")
        self.update_intervals = update_intervals
        self.alerts = []
        self.slack_poster = SlackPoster('Daemon Watcher')

    def run(self):
        while True:
            if os.path.exists('Daemon_PIDs'):
                for pid_file in os.listdir('Daemon_PIDs'):
                    name = '_'.join(pid_file.split('_')[1:])
                    if name in self.update_intervals:
                        modtime = os.path.getmtime(os.path.join('Daemon_PIDs', pid_file))
                        if time.time() - modtime > self.update_intervals[name] * 60.0:
                            self.alert(name)
                        else:
                            self.no_alert(name)
            else:
                pass  #can't find daemon pid folder. not sure when this would happen
            time.sleep(60)

    def alert(self, name):
        if name not in self.alerts:
            self.alerts.append(name)
            self.send_message(' '.join(('@channel', name, 'process is down!')))

    def no_alert(self, name):
        if name in self.alerts:
            self.alerts.remove(name)
            self.send_message(' '.join((name, 'process has resumed')))
            
    def send_message(self, message):
        self.slack_poster.send(message)
        
class AcousticDaemon(Daemon):
    def __init__(self,uiurl=5000,muxurl=9002,muxtype="cytec",pulserurl=9003, pulser="compact", scope='picoscope'):
        Daemon.__init__(self,self.run,name="easi_daemon")
        self.uiurl =  utils.parse_URL(uiurl)
        self.muxurl =  utils.parse_URL(muxurl)
        self.muxtype = muxtype
        self.pulserurl =  utils.parse_URL(pulserurl)
        self.acous = A.Acoustics(pulserurl=self.pulserurl,muxurl=self.muxurl,muxtype=muxtype,scope=scope)

    def run(self):
        while True:
            self.acous.beginRun()
            try:
                self.update_pid_time()
            except AttributeError:
                pass  # this happens if this class isn't inherited from Daemon
            
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
            if socket.gethostname() == 'ursamajor':
                ifname = 'eth2'
            else:
                ifname = 'eth0'
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            info = fcntl.ioctl(s.fileno(), 0x8927,  struct.pack('256s', ifname[:15].encode('utf-8')))
            hex_val =  ''.join(['%02x' % char for char in info[18:24]])
            mac_add = int(hex_val,16)

            try:
                table = json.loads(open("table_state.json").read())
            except FileNotFoundError:
                #initialize new table
                table = {"loop_delay" : "0", "last_tid": "0", "data" : []}
            table["mac"] = str(mac_add)[-4:]
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
            table = json.loads(open(os.path.join("../Data",startdate,"logfile.json")).read())
            ordered_table = collections.OrderedDict()
            ordered_table["data"] = collections.OrderedDict()
            for key in sorted(table["data"]):
                ordered_table["data"][key] = table["data"][key]
            return json.dumps(ordered_table)
            # return json.dumps(table) #get data for a given log

        @app.route('/table_save', methods=['GET', 'POST'])
        # @login_required
        def table_save():
            # if request.method == 'POST':
                out = {}
                try:
                    test = request.get_data().decode('utf-8')
                    open("table_state.json",'w').write(test)
                    out = json.loads(test)
                    out['status'] = 'success!'
                except Exception as E: 
                    out['status'] = str(E)
                socketio.emit('update_table') #tell the JS to update.
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
            try:
                files.remove('current.json')
            except:
                pass
            files = sorted(files)

            index = int(request.args.get('index', ''))
            data = json.load(open(os.path.join('../Data',start_date,testid,files[index])))
            framerate = data.get("framerate")
            print(framerate)
            if framerate == None:
                framerate = 1.25e8
            xs = [x*(1e6/framerate) for x in range(len(data['amp']))] #scale x to be in us
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

            #adding in waterfall plots.
            return json.dumps(out)

        @app.route('/<month>/<day>/<year>/<testid>/makewaterfall')
        @login_required
        def makewaterfall(month,day,year,testid):
            start_date = year + '_' + month + '_' + day
            l = filesystem.Loader()
            l.path = "../Data"
            waveset = l.load_waveset(testid,start_date,load_all=False)
            fig = plt.figure()
            waveset.plot_waterfall()
            waterfall = mpld3.fig_to_dict(fig)
            # plt.show(fig)
            out = {}
            out['fig02'] = waterfall
            # out['fig02'] = "False"]
            plt.close(fig)

            #adding in waterfall plots.
            return json.dumps(out)

        @socketio.on('test')
        def handle_test(data):
            socketio.emit('update', data) #tell the JS to update.

        @socketio.on('highlight')
        def active_row(rowid):
            socketio.emit('active', rowid)
                        
        while True:
            socketio.run(app,host="0.0.0.0",port=6054)  
       	#socketio.run(app,port=self.port)  
	
    def loadTools(self):
        pass

#class DBDaemon(Daemon):
class DBDaemon():
    def __init__(self,every_n_min=None):
        #Daemon.__init__(self,self.run,name="db_daemon")
        self.loader = filesystem.Loader()
        self.datapath = "../Data"
        self.loader.path = self.datapath
        self.n_min = every_n_min
        self.db = database.DB(host="25.18.5.52",port=5434,user="postgres")

        signal.signal(signal.SIGINT,  self.cleanobs)
        signal.signal(signal.SIGQUIT, self.cleanobs)
        signal.signal(signal.SIGTERM, self.cleanobs)

        self.wave_regex = re.compile("T[0-9]+p[0-9]+\.json")


    def modified_since(self,cutoff,path):
        """Takes a filepath, and recursively checks all folders/files for modifications.
        Warning: 2+ folders up won't detect a change in a file, only if it's created."""
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

    def check_all_dates(self,n_min):
        """Checks all the startdate folders contained in the Data folder. Returns a list of
        all the modified filepaths contained in the data path."""
        cutoff = time.time() - (n_min*60) #defaults to push files at same interval
        all_mod_files = []
        folders = os.listdir(self.datapath)
        folders.remove('Trash')
        for date_folder in folders:
            self.push_tests(os.path.join(self.datapath,date_folder,"logfile.json")) #make sure all the tests are in the 
            mod_files = self.modified_since(cutoff,os.path.join(self.datapath,date_folder))
            all_mod_files.extend(mod_files) #changed from append
        return all_mod_files


    def push_files(self,n_min):
        """Takes a list of modified files and loads them into corresponding Test and Wave objects.
        Test objects are returned when a logfile is modified, Waveset objects are returned when a 
        wave json file is added."""
        all_wavesets = {} #wavesets indexed by test ID
        all_tests = {}
        res = {}
        db = database.DB(host="25.18.5.52",port=5434,user="postgres")
        mod_files = self.check_all_dates(n_min)
        for mod_file in mod_files:
            file_names = mod_file.split("/")
            if file_names[-1] == "logfile.json":
                self.push_tests(mod_file)
            elif self.wave_regex.fullmatch(file_names[-1]) != None:
                #load wave from mod_file
                ###get the foldername of TestID_testid and cut off first part
                wave_test_id = file_names[-2][7:]
                # if self.check_test(mod_file,wave_test_id,"Fuji") == True:
                new_wave = self.loader.load_single_wave(mod_file,wave_test_id)
                # ws = data.Waveset(waves=[new_wave],wave_test_id)
                self.db.insert_waveset(ws,prevent_duplicates=False)
                # else:
                #     pass
            else:
                pass
        db.conn.close()
        del db

    def push_tests(self,logfile):
         #update tests from mod_file
        try:
            old_table = json.loads(open(logfile).read())
        except ValueError: #maybe caught while being edited? try again
            time.sleep(0.2) #if it fails this time, let if fail
            old_table = json.loads(open(logfile).read())
        new_table = self.loader.convert_names(old_table['data'])
        for entry in new_table:
            row = new_table[entry]
            new_test = data.Test(tabledata=row)
            # all_tests[row["test_id"]] = new_test
            self.db.insert_test(new_test)


    def write_last_check(self):
        """Keeps a running list of when the last time the db daemon updated"""
        # if os.path.exists("DB_push_status.txt") == False:
        with open("DB_push_status.txt", "a") as db_file:
            db_file.write(("Last Check Timestamp: %s\r\n") % (str(time.time())))
        return str(time.time())


    def cleanobs(self,*args):
        """Push all data since last observation before shutting down"""
        self.push_last()
        print("Attempting to push all data since last DB update")
        return

    def push_last(self):
        try:
            lines = [line.rstrip('\n') for line in open('DB_push_status.txt')]
        except FileNotFoundError:
            open('DB_push_status.txt',"w").write("0\n")
            lines = [line.rstrip('\n') for line in open('DB_push_status.txt')]
        tstamp = lines[-1].split("Last Check Timestamp: ")[-1] #extract timestamp from record
        timediff = (time.time() - float(tstamp))/60 #find time since last push and convert to min
        self.push_files(timediff+5) #5 min of buffer
        from_t = datetime.datetime.fromtimestamp(float(tstamp))
        to_t = datetime.datetime.fromtimestamp(time.time())
        self.write_last_check() #update the thing we just read
        print("Pushed all files since {} at {}".format(from_t,to_t))

    def run(self):
        while True:
            time.sleep(self.n_min*60)
            self.push_last()
        #stuff to do.

    def handler(self,fn): #need to reimplement this. right now it's stdin and stdout.
        try:
            fn()
        except:
            pass 

    def loadTools(self):
        pass



if __name__=="__main__":
#Timestamp of 12/5 1480924800.0
    #dbd = DBDaemon(.1)
    #dbd.run()
    #sys.exit()

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

    # wd = WatcherDaemon()
    # wd.start()
    # time.sleep(1)
    
    # dbd = DBDaemon(.1)
    # dbd.start()

    ad = AcousticDaemon(uiurl=port,muxurl=muxurl,muxtype="cytec",pulserurl=pulserurl)
    ad.start()
