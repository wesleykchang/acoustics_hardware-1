from pithy import *
from urllib import urlopen as uo
import libEpoch
import json

csvurl = 'http://localhost:9002/EPOCHmux.csv'
initurl = 'http://localhost:9002/EPOCHmux-init.csv'

def parsecsv(url):
    splits = uo(url).read().split("\n")
    header = splits.pop(0).replace('\"','')
    cols = header.split(",")
    out = []
    for i in splits:
        p = i.split(",")
        if i.lower().find("skip") == -1 and p[0].isdigit():
            out.append({})
            for j in range(len(p)):
                out[-1][cols[j]] = p[j] 
    return out

def switchmux(chan):
    try:
        uo("http://localhost:9003/write/%i" % int(chan)).read()
    except:
        error = 'WARNING: No channel %s on this mux' % q['Channel']
        print error
    
def getSingleData(q,isTE=False):
    if isTE:
        label = "TR"
        func = ep.commanderTrans
    else:
        label = "PE"
        func = ep.commanderPE
    #print label
    try:
        fn = pre+"%s_%s_%s_%i.json" % (q['Name'],q['Channel'],label,int(time.time()))
        data = func(gain=float(q[label+' Gain (dB)']),
                    tus_scale=int(q[label+' Time (us)']),
                    freq=float(q['Freq (MHz)']))
        rtime = [round(x,3) for x in list(data[0])]
        json.dump({'time (us)':rtime,'amp':list(data[1])}, open(fn,'w'))
    except:
        print '***ERROR***'
        import traceback
        print traceback.format_exc()

ep = libEpoch.epoch("http://localhost:9004")

#mux map -> fixed to whatever it is for real
mm = {} 
mm[1] = 23
mm[2] = 25
mm[3] = 27
mm[4] = 29
mm[5] = 31
mm[6] = 33
mm[7] = 35
mm[8] = 37

pre = "/home/pi/acoustic/data/"

init = False
while True:
    if init:
        queue = parsecsv(initurl)
        init = False
    else:
        queue = parsecsv(csvurl)
    for q in queue:
        #print q
        if q['Mode tr/pe/both'].lower() in ['tr','both']:
            switchmux(mm[int(q['Channel'])])
            getSingleData(q,True)
        if q['Mode tr/pe/both'].lower() in ['pe','both']:
            switchmux(mm[int(q['Channel'])]-1)
            getSingleData(q,False)