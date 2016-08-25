###################################################
###################################################
##    import this library, not libepoch or     ##
##    whatever else                     ##
###################################################
###################################################

#normal libs
from urllib.request import urlopen as uo
import json
import libCompactPR
import os
import datetime
import time
#in this package
import libEpoch
import oldmux as omux
import cytec
from pprint import pprint
from http.server import SimpleHTTPRequestHandler
import socketserver
from socketIO_client import SocketIO, LoggingNamespace
import matplotlib.pyplot as plt
import numpy as np

def debug(s):
    print("[libacoustic] "+s)

class Acoustics():
    def __init__(self,muxurl=None,muxtype=None,pulser="compact",pulserurl=None):
        self.path = os.getcwd()
        self.pulser = pulser.lower()
        print(self.pulser)
        #can be fixed by checking if folder exists, and appending a number to the end

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
            self.p = libCompactPR.CP(pulserurl,rp_url="169.254.134.177")

         # if muxurl is None:
         #  print("------------------------------------------------")
         #  print("WARNING: No mux given. Ignoring channel numbers.")
         #  print("------------------------------------------------")

    def getJSON(self):
        """Reads in a json from json_file. JSON contains
        parameter settings and experiment details"""
        #no real reason to do this via web if the file is local

        settings = json.load(open("table_state.json"))

        #convert the start date to string with MM_DD to be used for filename
        for row in settings['data']:
            row['date_fname'] = (row['startdate'])[0:11].replace(" ", "_")
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

    def writeLog(self,row):
        """Attempts to open a log file and add the row to it. If there is no logfile, creates one."""
        logname = os.path.join(self.path,"Data",row['date_fname'],"logfile.json") #path to logfile
        try:
            info = json.load(open(logname))
            info['data'].append(row) #append to the list of dicts
            json.dump(info, open(logname, 'w'))

        except FileNotFoundError: #first entry in the logfile, need to create one.
            info = {'data' : []}
            info['data'].append(row) #append to the list of dicts
            json.dump(info, open(logname, 'w'))

    def saveData(self,data,row,fsweep):
        """Stores data as JSON files named by time in Data/StartDate/TestID"""
        #misc path generation
        row_name = "TestID_" + row['testid']
        fname = os.path.join(self.path,"Data",row['date_fname'],row_name,str(time.time()).replace(".","_") + ".json")
        fname_current = os.path.join(self.path,"Data",row['date_fname'],row_name,"current.json")

        if fsweep == True:
            fname = os.path.join(self.path,"Data",row['date_fname'],row_name,"F" + str(row["freq(mhz)"]) + "_T" + str(time.time()).replace(".","_") + ".json")

        try:
            json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
            json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname_current,'w'))
        except FileNotFoundError:
            #brand new row. initialize it and name it, then try dumping file
            os.makedirs(os.path.join("Data",row['date_fname'],row_name))
            json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
            json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname_current,'w'))
            self.writeLog(row) #since this is the first time a row is intialized, it enters it to logfile


    def getSingleData(self,row,fsweep=False):
        """Processes a single row/test from the table. each row is a dictionary. Forwards command to
        Epoch and stores a json waveform in a folder that corresponds to the row."""
        
        if self.mux is not None:
            if row['channel2']!="":
                self.mux.switch(row['channel'],row['channel2'])
            else:
                self.mux.switch(row['channel'])

        try:
            data = self.p.commander(row)
            self.saveData(data,row,fsweep)
            self.socketIO.emit('test',{"rowid":row["testid"],"amp":data[1]},broadcast=True) #send sparkline
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
                    self.socketIO = SocketIO('localhost', 5000, LoggingNamespace)
                    self.socketIO.emit('highlight',{"rowid":row["testid"]}, broadcast=True)

                    fs = row["freq(mhz)"].split(",")

                    if len(fs) == 1:
                        self.getSingleData(row)
                    elif len(fs) == 3:
                        flist = np.linspace(int(fs[0]),int(fs[1]),int(fs[2]))
                        for freq in flist:
                            row["freq(mhz)"] = freq
                            print(row["freq(mhz)"])
                            self.getSingleData(row,fsweep=True)
                except:
                    import sys
                    t,v,tb = sys.exc_info()
                    print(t)
                    print(v)
                time.sleep(.1) #needed to give the table_state a chance to update

            elif row['run(y/n)'] == 'n':
                counter += 1
                if counter==(len(tests['data'])):
                    time.sleep(1) #artificial delay. if all the rows are set to 'n'. otherwise it dies

        # if not loop: break

if __name__=="__main__":
    a = Acoustics(pulserurl="http://localhost:9001", muxurl="http://localhost:9000", muxtype="cytec")
    a.beginRun(loop=False)
    # a.getJSON()






















