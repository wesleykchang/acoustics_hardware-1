from pithy import *
import json 

path = '/Users/j125mini/EASI/data/'

pat = '''20160229-arpaedemo-AA-cell1
'''

pat = pat.split('\n')

for nm in pat:
    top = glob(path + "%s*.json" % nm)
    top.sort()
    
    bigdextop = []
    
    for i in top:
        ts = i.split("_")[-1].replace(".json","")
        f = json.load(open(i))
        bigdextop.append(abs(array(f['amp'])-32639))
    
    #subplot(311)
    bigdextop = array(bigdextop).transpose()
    pod = imshow(bigdextop,aspect="auto")
    #ylabel('Top Position')
    title(nm)
    
    showme()
    clf()