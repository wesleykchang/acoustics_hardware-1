###################################################
###################################################
##    import this library, not libepoch or     ##
##    whatever else                     ##
###################################################
###################################################

#normal libs
from urllib.request import urlopen as uo
import json
import libEpoch
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

def debug(s):
    print("[libacoustic] "+s)

class Acoustics():
    def __init__(self,muxurl=None,muxtype=None,pulser="epoch",pulserurl=None):
        self.path = os.getcwd()
        self.socketIO = SocketIO('localhost', 5000, LoggingNamespace)
        #can be fixed by checking if folder exists, and appending a number to the end

        if muxurl is not None and muxtype is not None:
            if muxtype.lower()=="cytec":
                self.mux = cytec.Mux(self.cleanURL(muxurl))
            elif ["old","oldmux"].count(muxtype.lower())>0:
                self.mux = omux.Mux(self.cleanURL(muxurl))
        else:
           self.mux = None
        if pulserurl:
            self.pulserurl = self.cleanURL(pulserurl)
        if muxurl is None:
           print("------------------------------------------------")
           print("WARNING: No mux given. Ignoring channel numbers.")
           print("------------------------------------------------")
           
        if pulser.lower()=="epoch":
            self.pulser="epoch"
            print("connecting to Epoch...")
            self.p = libEpoch.Epoch(pulserurl)
            print("... done!")

         # if muxurl is None:
         #  print("------------------------------------------------")
         #  print("WARNING: No mux given. Ignoring channel numbers.")
         #  print("------------------------------------------------")

    def getJSON(self):
        """Reads in a json from json_file. JSON contains
        parameter settings and experiment details"""
        #no real reason to do this via web if the file is local

        settings = json.loads(open("table_state.json").read())

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

    def getSingleData(self,row):
        """Processes a single row/test from the table. each row is a dictionary. Forwards command to
        Epoch and stores a json waveform in a folder that corresponds to the row."""

        #misc path generation
        row_name = "TestID_" + row['testid']

        # try:
        #    os.mkdir(os.path.join(self.folder_name, row_name))
        # except FileExistsError:
        #    pass

        row_name = "TestID_" + row['testid']
        fname = os.path.join(self.path,"Data",row['date_fname'],row_name,str(time.time()).replace(".","_") + ".json")
        fname_current = os.path.join(self.path,"Data",row['date_fname'],row_name,"current.json")
        
        if self.mux is not None:
            if row['channel2']!="":
                self.mux.switch(row['channel'],row['channel2'])
            else:
                self.mux.switch(row['channel'])

        if self.pulser=="epoch":
            try:
                data = self.p.commander(
                    isTR=row['mode(tr/pe)'].lower(),
                    gain=float(row['gain(db)']),
                    tus_scale=int(row['time(us)']),
                    freq=float(row['freq(mhz)']),
                    delay=float(row['delay(us)']),
                    filt=float(row['filtermode']))
                try:
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname_current,'w'))
                except FileNotFoundError:
                    #brand new row. initialize it and name it, then try dumping file
                    os.makedirs(os.path.join("Data",row['date_fname'],row_name))
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname_current,'w'))
                    self.writeLog(row) #since this is the first time a row is intialized, it enters it to logfile
                return data
            except:
                print('***ERROR***')
                import traceback
                print(traceback.format_exc())

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

    
    def beginRun(self,loop=True):
        """Loops through the rows and processes each one"""
        index = 0 #counter to keep track of the row number. Temporary, to be replaced with TestID
        tests = self.getJSON()
        # while True: 
        for row in tests['data']:
            if (row['run(y/n)']).lower() == 'y':
                #print("Executing row "+str(i+1))
                data = self.getSingleData(row)
                self.socketIO.emit('test',{"rowid":row["testid"],"amp":list(data[1])},broadcast=True)
                self.socketIO.wait(seconds=1)
            else:
                pass
        # if not loop: break

if __name__=="__main__":
    a = Acoustics(pulserurl="http://localhost:9001", muxurl="http://localhost:9000", muxtype="cytec")
    a.beginRun(loop=False)
    # a.getJSON()






















