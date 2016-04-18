from pithy import *
import json
import glob

datat = json.load(open(glob.glob("/home/pi/acoustic/data/pooper_2_TR*")[-1],'r'))
datap = json.load(open(glob.glob("/home/pi/acoustic/data/pooper_2_PE*")[-1],'r'))

plot(datat[u'time (us)'],datat[u'amp'])
title("TR")
showme()
clf()
plot(datap[u'time (us)'],datap[u'amp'])
title("PE")
showme()
clf()