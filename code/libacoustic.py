###################################################
###################################################
##      import this library, not libepoch or     ##
##      whatever else                            ##
###################################################
###################################################

from pithy import *
from urllib import urlopen as uo
import json
import libSIUI as siui
import libEpoch
import libethercalc as ether
from time import sleep

class Acoustics():
    def __init__(self,muxurl=None,etherurl=None,pulser=None,pulserurl=None):
        self.pre = "/Users/j125mini/EASI/data/"
        if muxurl:
            self.muxurl = self.cleanURL(muxurl)
        else:
            self.muxurl = None
        if pulserurl:
            self.pulserurl = self.cleanURL(pulserurl)
        if etherurl is not None:
            self.ether = ether.Ether(etherurl)
        else:
            print "-----------------------------------------"
            print "WARNING: No ethercalc. Stuff might break."
            print "-----------------------------------------"
        if muxurl is None:
            print "------------------------------------------------"
            print "WARNING: No mux given. Ignoring channel numbers."
            print "------------------------------------------------"
            
        if pulser.lower()=="epoch":
            self.pulser="epoch"
            print "connecting to Epoch..."
            self.p = libEpoch.epoch(pulserurl)
            print "... done!"
        elif pulser.lower()=="siui":
            self.pulser="siui"
            print "connecting to SIUI..."
            self.p = siui.SIUI(pulserurl)
            print "... done!"
        else:
            raise AttributeError("no valid pulser type given!")
            
    def cleanURL(self,url):
        if url[-1]=="/":
            return url[:-1]
        else:
            return url
            
    def switchMux(self,chan,chan2=None):
        try:
            if chan2 is None:
                u = self.muxurl+"/write/%i" % int(chan)
                print 'chan1=', chan , 'chan2=',chan2
            else:
                u = self.muxurl+"/write/%i,%i" % (int(chan),int(chan2))
                print 'chan1=', chan , 'chan2=',chan2
            uo(u).read()
            sleep(0.5)
        except:
            print "problem with mux"

    def mark_time(self):
        mark = time.time() - self.start_time
        print mark
        return mark
    
    def getSingleData(self,row):
        self.start_time = time.time()
        
        q = row
        
        # print q['Name']
        print q['Channel']
        # print q['Mode (tr/pe)'].upper()
        # print int(time.time())
        fn = self.pre+"%s_%s_%s_%i.json" % (q['Name'],q['Channel'],q['Mode (tr/pe)'].upper(),int(time.time()))
        
        if self.muxurl is not None:
            if q['Channel 2']!="":
                self.switchMux(q['Channel'],q['Channel 2'])
                print 'tr'
            else:
                self.switchMux(q['Channel'])
                print 'pe'
        # else:
        #     print 'nomux'
        if self.pulser=="epoch":
            try:
                data = self.p.commander(
                    isTR=q['Mode (tr/pe)'].lower(),
                    gain=float(q['Gain (dB)']),
                    tus_scale=int(q['Time (us)']),
                    freq=float(q['Freq (MHz)']),
                    delay=float(q['Delay (us)']))
                json.dump({'time (us)':list(data[0]),'amp':list(data[1]),'gain':float(q['Gain (dB)'])}, open(fn,'w'))
                return data
            except:
                print '***ERROR***'
                import traceback
                print traceback.format_exc()
        elif self.pulser=="siui":
            vel = 4000 #m/s
            pw = 1/(float(q['Freq (MHz)'])*1E6)*1E9
            rng = (float(q['Time (us)'])/1E6)*vel*1000.0
            self.p.params['range'] = int(rng)
            self.p.params['vset'] = 400 #pulse voltage
            self.p.params['pw'] = int(floor(pw/10)*10)
            self.p.params['vel'] = int(vel)
            #s.params['rect'] = 'rf'#rectification
            self.p.params['prf'] = 400  #repitition frequency
            self.p.params['gain'] = q['Gain (dB)']
            self.p.params['mode'] = q['Mode (tr/pe)'].upper()
            data = self.p.setGetCheck()
            sleep(6)
            data = self.p.getData()
            rtime = [round(float(x)/(vel*1E3),3) for x in list(data['x'])]
            out = {'time (us)':rtime,'amp':[int(x) for x in list(data['wave'])],'gain':q['Gain (dB)']}
            json.dump(out, open(fn,'w'))
            time.sleep(0.2)
            
            # print "execution time: ",
            # extime = self.mark_time()
            # print extime
            # open(self.pre + q['Name']+'extime',"a").write(str(extime)+",")
            
            return data
    
    def beginRun(self,loop=True):
        while True: 
            self.ether.refresh()
            for i in range(len(self.ether.rows)-1):
                r = self.ether.rows[i]
                # print r
                if r['Run (y/n)'].lower() == 'y':
                    print "Executing row "+str(i+1)
                    self.getSingleData(r)
                else:
                    pass
            if not loop: break

if __name__=="__main__":
    # a = Acoustics(pulser="siui",pulserurl="http://localhost:9000",muxurl="http://localhost:9001")
    
    # d1 = a.getSingleData({'Name':"fakefakefake",'Channel':2,'Channel 2':8,'Gain (dB)':62,'Freq (MHz)':2.25,'Mode (tr/pe)':"TR",'Time (us)':12, 'Delay (us)':0})
    # # print d1[0]
    # plot(d1['x'],d1['wave'])
    # showme()
    # clf()
    print 1

























