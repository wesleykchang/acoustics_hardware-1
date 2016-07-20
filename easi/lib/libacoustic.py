###################################################
###################################################
##      import this library, not libepoch or     ##
##      whatever else                            ##
###################################################
###################################################

#normal libs
from urllib.request import urlopen as uo
import json
import libSIUI as siui
import libEpoch
import libethercalc as ether
import os
import datetime
import time
#in this package
import libSIUI as siui
import libEpoch
import libethercalc as ether
from mux import Mux
from pprint import pprint

def debug(s):
    print("[libacoustic] "+s)

#URLs: Table URL is here: http://feasible.io:8180
#JSON is output here: http://feasible.pithy.io:4011/table_load


class Acoustics():
    def __init__(self,muxurl=None,json_url=None,pulser="epoch",pulserurl=None):
        self.path = os.getcwd()
        self.json_url = json_url
        self.folder_name = str(datetime.date.today()) #might be a problem if multiple exps are run on same day
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

    def getJSON(self):
        """Reads in a json from json_file. JSON contains
        parameter settings and experiment details"""
        json_file = uo(self.json_url)
        json_file_str = json_file.readall().decode('utf-8')
        settings = json.loads(json_file_str)
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
    
    def getSingleData(self,row, row_no):
        """Processes a single row/test from the table. each row is a dictionary. Forwards command to
        Epoch and stores a json waveform in a folder that corresponds to the row."""

        ###Might be a better way to keep track of row number, maybe output it as part of the JSON.
        ###

        row_name = "Row_" + str(row_no)
        os.mkdir(os.path.join(self.folder_name, row_name))
        fname = os.path.join(self.path,self.folder_name,row_name,str(time.time()))
        
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
                json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(row['gain(db)'])}, open(fname,'w'))
                return data
            except:
                print('***ERROR***')
                import traceback
                print(traceback.format_exc())
    
    def beginRun(self,loop=True):
        """Loops through the rows and processes each one"""
        index = 0 #counter to keep track of the row number. Temporary, to be replaced with TestID
        tests = self.getJSON()
        os.mkdir(self.folder_name)
        # while True: 
        for row in tests['data']:
            if (row['run(y/n)']).lower() == 'y':
                #print("Executing row "+str(i+1))
                self.getSingleData(row, index)
            else:
                pass
            index += 1
        # if not loop: break

if __name__=="__main__":
    # a = Acoustics(pulser="siui",pulserurl="http://localhost:9000",muxurl="http://localhost:9001")
    # d1 = a.getSingleData({'Name':"fakefakefake",'Channel':2,'Channel 2':8,'Gain (dB)':62,'Freq (MHz)':2.25,'Mode (tr/pe)':"TR",'Time (us)':12, 'Delay (us)':0})
    # # print(d1[0])
    # plot(d1['x'],d1['wave'])
    # showme()
    # clf()
    # print(1)

    a = Acoustics(json_url= "http://feasible.pithy.io:4011/table_load",pulserurl="9003")
    a.beginRun(loop=False)
    # params = a.getJSON()
    # pprint(params)
    # pprint(params["data"])

























