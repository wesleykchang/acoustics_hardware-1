###################################################
###################################################
##      import this library, not libepoch or     ##
##      whatever else                            ##
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
from mux import Mux
from pprint import pprint
from http.server import SimpleHTTPRequestHandler
import socketserver

def debug(s):
    print("[libacoustic] "+s)

#URLs: Table URL is here: http://feasible.io:8180
#JSON is output here: http://feasible.pithy.io:4011/table_load


class Acoustics():
    def __init__(self,muxurl=None,json_url=None,pulser="epoch",pulserurl=None):
        self.path = os.getcwd()
        self.json_url = json_url
        #can be fixed by checking if folder exists, and appending a number to the end

        # if muxurl:
        #     self.mux = m.Mux(self.cleanURL(muxurl),fake=fake)
        # else:
        #     self.mux = None
        # if pulserurl:
        #     self.pulserurl = self.cleanURL(pulserurl)
        # if muxurl is None:
        #     print("------------------------------------------------")
        #     print("WARNING: No mux given. Ignoring channel numbers.")
        #     print("------------------------------------------------")
            
        if pulser.lower()=="epoch":
            self.pulser="epoch"
            print("connecting to Epoch...")
            self.p = libEpoch.Epoch(pulserurl)
            print("... done!")

         # if muxurl is None:
         #    print("------------------------------------------------")
         #    print("WARNING: No mux given. Ignoring channel numbers.")
         #    print("------------------------------------------------")

    def getJSON(self):
        """Reads in a json from json_file. JSON contains
        parameter settings and experiment details"""
        json_file = uo(self.json_url)
        json_file_str = json_file.readall().decode('utf-8')
        settings = json.loads(json_file_str)

        #temporary until startdates are generated & sent by js file.
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

        ###Later row will be replaced with testID

        row_name = "TestID_" + row['testid']
        # try:
        #     os.mkdir(os.path.join(self.folder_name, row_name))
        # except FileExistsError:
        #     pass

        fname = os.path.join(self.path,"Data",row['startdate'],row_name,str(time.time()).replace(".","_") + ".json")
        fname_current = os.path.join(self.path,"Data",row['startdate'],row_name,"current.json")
        
        # if self.mux is not None:
        #     if row['channel2']!="":
        #         self.mux.switch(row['channel'],row['channel2'])
        #     else:
        #         self.mux.switch(row['channel'])

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
                    os.makedirs(os.path.join("Data",row['start_date'],row_name))
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
                    json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname_current,'w'))

                return data
            except:
                print('***ERROR***')
                import traceback
                print(traceback.format_exc())
    
    def beginRun(self,loop=True):
        """Loops through the rows and processes each one"""
        index = 0 #counter to keep track of the row number. Temporary, to be replaced with TestID
        tests = self.getJSON()
        # while True: 
        for row in tests['data']:
            if (row['run(y/n)']).lower() == 'y':
                #print("Executing row "+str(i+1))
                self.getSingleData(row)
            else:
                pass
        # if not loop: break

if __name__=="__main__":
    a = Acoustics(json_url= "http://localhost:5000/table_load",pulserurl="9003")
    a.beginRun(loop=False)
    # a.getJSON()






















