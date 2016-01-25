from pithy import *
from urllib import urlopen as uo
import libEpoch
import json

def parseGoog():
    splits = uo(url).read().split("\n")
    header = splits.pop(0)
    cols = header.split(",")
    out = []
    for i in splits:
        p = i.split(",")
        if i.lower().find("skip") == -1 and p[0].isdigit():
            out.append({})
            for j in range(len(p)):
                out[-1][cols[j]] = p[j] 
    return out

key = "1vxDftE5BdR7c8bSdvlU2Q3JAdjR6T3vrz_U6URW9qgo"
url = "https://docs.google.com/spreadsheets/d/%s/export?format=csv"% key

ep = libEpoch.epoch("http://localhost:9001")

pre = "/Users/lab/Documents/epochdata/"


while True:
    try:
        queue = parseGoog()
    except:
        pass
    for q in queue:
            
        try:
            if q['runTR'].find('yes') > -1:
                fn = pre+"%s_%s_TR_%i.json" % (q['Name'],q['Channel'],int(time.time()))
                data = ep.commanderTrans(gain=int(q['TR Gain (dB)']),delay=float(q['TR delay (us)']),tus_scale=float(q['TR Time (us)']),freq=float(q['Freq (MHz)\r']))
                json.dump(
                    {'time (us)':list(data[0]),'amp':list(data[1])},
                    open(fn,'w'))
            
            if q['runPE'].find('yes') > -1:
                fn = pre+"%s_%s_PE_%i.json" % (q['Name'],q['Channel'],int(time.time()))
                data = ep.commanderPE(gain=int(q['PE Gain (dB)']),delay=float(q['PE delay (us)']),tus_scale=float(q['PE Time (us)']),freq=float(q['Freq (MHz)\r']))
                json.dump(
                    {'time (us)':list(data[0]),'amp':list(data[1])},
                    open(fn,'w'))
        except:
            error = 'Something bad happened on %s at %s' % (time.strftime("%a %b %d %Y", time.gmtime()), time.strftime("%H:%M:%S", time.gmtime()))
            print error  
            pass