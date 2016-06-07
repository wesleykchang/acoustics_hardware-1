from pithy import *
import json 

path = '/Users/j125mini/EASI/data/standards/'

pat = '''PS-siui
Ac-siui
PS-olympus
Ac-olympus'''

# pat = "poooooooop"
tit = ['Polystyrene 1/8"\nSIUI trandsducers', 'Acrylic 1/4"\nSIUI trandsducers', 'Polystyrene 1/8"\nOlympus trandsducers','Acrylic 1/4"\nOlympus trandsducers']

pat = pat.split('\n')

count = 0 
for nm in pat:
    for pul in ['TR','PE']:
        top = glob(path + "%s*set1*%s*.json" % (nm,pul))
        top.sort()
        mid = glob(path + "%s*set2*%s*.json" % (nm,pul))
        mid.sort()
        bot = glob(path + "%s*set3*%s*.json" % (nm,pul))
        bot.sort()
        
        print len(top)
        print len(mid)
        print len(bot)
        
        bigdex1 = []
        bigdex2 = []
        bigdex3 = []
        tofdex1 = []
        tofdex2 = []
        tofdex3 = []
        
        for i in top:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdex1.append(abs(array(f['amp'])-127))
        tofdex1.append(array(f['time (us)']))
        for i in mid:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdex2.append(abs(array(f['amp'])-127))
        tofdex2.append(array(f['time (us)']))
        for i in bot:
            ts = i.split("_")[-1].replace(".json","")
            f = json.load(open(i))
            bigdex3.append(abs(array(f['amp'])-127))
        tofdex3.append(array(f['time (us)']))
        
        if pul == 'TR':
            subplot(321)
            bigdex1 = array(bigdex1).transpose()
            tofdex1 = array(tofdex1).transpose()
            plot(tofdex1,bigdex1)
            annotate('Transducer Set 1',xy=(5,100))
            ylabel('Acoustic Intensity\n(A.U.)')
            title(tit[count] + ' - ' + pul)
            
            subplot(323)
            bigdex2 = array(bigdex2).transpose()
            tofdex2 = array(tofdex2).transpose()
            plot(tofdex2,bigdex2)
            annotate('Transducer Set 2',xy=(5,100))
            ylabel('Acoustic Intensity\n(A.U.)')
            
            subplot(325)
            bigdex3 = array(bigdex3).transpose()
            tofdex3 = array(tofdex3).transpose()
            plot(tofdex3,bigdex3)
            annotate('Transducer Set 3',xy=(5,100))
            ylabel('Acoustic Intensity\n(A.U.)')
            xlabel('Time of Flight (us)')
        if pul == 'PE':
            subplot(322)
            bigdex1 = array(bigdex1).transpose()
            tofdex1 = array(tofdex1).transpose()
            plot(tofdex1,bigdex1)
            annotate('Transducer Set 1',xy=(2,100))
            # ylabel('Acoustic Intensity\n(A.U.)')
            title(tit[count] + ' - ' + pul)
            
            subplot(324)
            bigdex2 = array(bigdex2).transpose()
            tofdex2 = array(tofdex2).transpose()
            plot(tofdex2,bigdex2)
            annotate('Transducer Set 2',xy=(2,100))
            # ylabel('Acoustic Intensity\n(A.U.)')
            
            subplot(326)
            bigdex3 = array(bigdex3).transpose()
            tofdex3 = array(tofdex3).transpose()
            plot(tofdex3,bigdex3)
            annotate('Transducer Set 3',xy=(2,100))
            # ylabel('Acoustic Intensity\n(A.U.)')
            xlabel('Time of Flight (us)')
        
    showme()
    clf()
        
    count += 1