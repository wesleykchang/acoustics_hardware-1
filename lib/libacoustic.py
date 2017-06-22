################################################
################################################
##    import this library, not libepoch or    ##
##    whatever else                           ##
################################################
################################################

#normal libs
from urllib.request import urlopen as uo
import json
import libCompactPR
import os
import datetime
import time
import sys
#in this package
sys.path.append('../EASI-analysis/analysis') #add saver functions to path
import filesystem
import libEpoch
import oldmux as omux
import cytec
from pprint import pprint
import socketserver
from socketIO_client import SocketIO, BaseNamespace,LoggingNamespace
import matplotlib.pyplot as plt
import numpy as np
import database as db
import signal

# Register a handler for the timeout
def handler(signum, frame):
   print ("Exiting socket call, taking too long...")
   raise Exception("Socket call blocking")


class Acoustics():
    def __init__(self,muxurl=None,muxtype=None,pulser="compact",pulserurl=None,scope='picoscope'):
        self.path = os.getcwd()
        self.pulser = pulser.lower()
        self.enable_sockets = True

        signal.signal(signal.SIGALRM, handler) #alarm to timeout on blocking funcs
        if self.enable_sockets:
            try:
                signal.alarm(5)
                self.sio =  SocketIO('localhost', 6054, LoggingNamespace)
                signal.alarm(0)
            except:
                self.enable_sockets = False
                pass
        self.saver = filesystem.Saver()
        self.scope = scope
        
        if muxurl is not None and muxtype is not None:
            if muxtype.lower()=="cytec":
                self.mux = cytec.Mux(self.cleanURL(muxurl))
            elif ["old","oldmux"].count(muxtype.lower())>0:
                self.mux = omux.Mux(self.cleanURL(muxurl))
            else:
                self.mux = None
        else:
           self.mux = None
        if pulserurl:
            self.pulserurl = self.cleanURL(pulserurl)
        if muxurl is None:
           print("------------------------------------------------")
           print("WARNING: No mux given. Ignoring channel numbers.")
           print("------------------------------------------------")
           
        if self.pulser=="epoch":
            print("connecting to Epoch...")
            self.p = libEpoch.Epoch(pulserurl)
            print("... done!")
        elif self.pulser == "compact":
            self.p = libCompactPR.CP(pulserurl, scope=self.scope)


    def getJSON(self):
        """Reads in a json from json_file. JSON contains
        parameter settings and experiment details"""
        #no real reason to do this via web if the file is local

        settings = json.load(open("table_state.json"))

        months =   {'Jan' : '01', 'Feb' : '02' ,
                    'Mar' : '03', 'Apr' : '04' ,
                    'May' : '05', 'Jun' : '06' ,
                    'Jul' : '07', 'Aug' : '08' ,
                    'Sep' : '09', 'Oct' : '10' ,
                    'Nov' : '11', 'Dec' : '12' }

        #convert the start date to string with MM_DD to be used for filename
        for row in settings['data']:
            if row["startdate"] != "":
                mo, day, year = (row['startdate'])[0:11].split(" ")
                row['date_fname'] = year + "_" + months[mo] + "_" + day
        return settings
            
    def cleanURL(self,url):
        if url[-1]=="/":
            return url[:-1]
        else:
            return url

    def mark_time(self):
        mark = time.time() - self.start_time
        print(mark)
        return mark

    def getSingleData(self,row,fsweep=None):
        """Processes a single row/test from the table. each row is a dictionary. Forwards command to
        Epoch and stores a json waveform in a folder that corresponds to the row."""
        
        if self.mux is not None:
            if row['channel2']!="":
                self.mux.switch(row['channel'],row['channel2'])
            else:
                self.mux.switch(row['channel'])

        try:
            data = self.p.commander(row)
            self.saver.saveData(data,row,fsweep)
            if self.enable_sockets:
                try:
                    signal.alarm(5) #give the socket 5 seconds to execute before raising exception
                    self.sio.emit('test',{"rowid":row["testid"],"amp":data[1]}) #send sparkline
                    signal.alarm(0) #disable alarm if code exits in time
                except:
                    self.enable_sockets = False
                    pass
            return data
        except:
            print('***ERROR***')
            import traceback
            print(traceback.format_exc())
    
    def beginRun(self,loop=True):
        """Loops through the rows and processes each one"""
        tests = self.getJSON()
        # while True: 
        counter = 0 #keeps track of inactive rows
        for row in tests['data']:
            if (row['run(y/n)']).lower() == 'y':
                try:
                    print("testing%s" % str(row['testid']))
                    if self.enable_sockets:
                        try:
                            signal.alarm(5) #give the socket 5 seconds to execute before raising exception
                            self.sio.emit('highlight',{"rowid":row["testid"]})
                            signal.alarm(0) #disable alarm if code exits in time
                        except:
                            self.enable_sockets = False
                            pass

                    fs = row["freq(mhz)"].split(",")

                    if len(fs) == 1:
                        self.getSingleData(row)
                    elif len(fs) == 3:
                        flist = np.linspace(float(fs[0]),float(fs[1]),int(fs[2]))
                        sweept = time.time()
                        for freq in flist:
                            row["freq(mhz)"] = freq
                            self.getSingleData(row,fsweep=[sweept,fs])
                except:
                    import sys
                    t,v,tb = sys.exc_info()
                    print(t)
                    print(v)
                time.sleep(.1) #needed to give the table_state a chance to update

            else:
                counter += 1
                if counter==(len(tests['data'])):
                    if self.enable_sockets:
                        try:
                            signal.alarm(5) #give the socket 5 seconds to execute before raising exception
                            self.sio.emit('highlight',{"rowid":'inactive'})
                            signal.alarm(0) #disable alarm if code exits in time
                        except:
                            self.enable_sockets = False
                            pass
                    time.sleep(1) #artificial delay. if all the rows are set to 'n'. otherwise it dies

        time.sleep(float(tests['loop_delay']))

        # if not loop: break

if __name__=="__main__":
    a = Acoustics(pulserurl="http://localhost:9001", muxurl="http://localhost:9000", muxtype="cytec")
    a.beginRun(loop=False)
    # a.getJSON()






















