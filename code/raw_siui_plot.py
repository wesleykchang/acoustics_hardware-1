from pithy import *
import json 
from urllib import urlopen as uo

raw =[x.strip().split(",") for x in open("/home/lab/EASI/data/ugh","r").readlines()]

out = []
for r in raw[1:]:
    l = []
    for i in range(len(r)):
        try:
            l.append(abs(int(raw[0][i])-int(r[i])))
        except:
            pass
    out.append(l)
    out.append(l)
    out.append([0 for x in range(len(l))])
    
    

a = imshow(out,aspect="auto")
xlim(0,4000)
#ylim(200,100)
showme()
clf()

print min(out[250]),max(out[250])