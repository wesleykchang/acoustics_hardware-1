from pithy import *
from MTI_Tools import *
import time
import matplotlib.gridspec as gridspec
import simplejson as json

figure(figsize=(10, 8))
gs = gridspec.GridSpec(29, 1)
ax_pot = plt.subplot(gs[20:24,0])
ax_cur = plt.subplot(gs[25:29,0])
ax_pe = plt.subplot(gs[0:9,0])
ax_tr = plt.subplot(gs[10:19,0])

echem = '/Users/j125mini/Downloads/TC5.4/_COM7/data/AH/'
fil = 'AH_20160301_081529_07_1.nda'

ac = '/Users/j125mini/EASI/data/20160301-arpaedemo-AA-cell3'

###########################
#########ECHEM DATA########

path = echem
data = mti_data(path+fil)

#cols:: 1:cyc# 3:TestTime 5:Amp-hr(capacity_passed) 7:Amps 8:Volt 9:State(R=rest,D=disch,C=char) 10:ES(0 looks like step change)
#data = genfromtxt(path+fil,delimiter = '\t', skip_header = 5,usecols=(1,3,5,7,8,9,10),dtype=None)

cyc = data['cycle']
tim = data['time']
cap = data['capacity_passed']
cur = data['current']
pot = data['potential']
ste = []
dst = []

ax_pot.plot(array(tim)/3600,pot)
ax_pot.set_ylabel('Volts')
ax_pot.set_xticks([])
ax_cur.plot(array(tim)/3600,cur)
ax_cur.set_ylabel('Amps')
ax_cur.set_xlabel('Cycling Time (hr)')
ax_cur.set_ylim(min(cur)*1.1,max(cur)*(1.1))



##################################
#########Acoustic Data############


tr = glob(ac + "*TR*.json")
tr.sort()
pe = glob(ac + "*PE*.json")
pe.sort()

bigdextr = []
bigdexpe = []

for i in tr:
    ts = i.split("_")[-1].replace(".json","")
    f = json.load(open(i))
    bigdextr.append(abs(array(f['amp'])-127))
for i in pe:
    ts = i.split("_")[-1].replace(".json","")
    f = json.load(open(i))
    bigdexpe.append(abs(array(f['amp'])-127))
    
#tof = f['time (us)']

bigdextr = array(bigdextr).transpose()
bigdexpe = array(bigdexpe).transpose()

#tickpt  = [0,99,165,231,396,494]
#TR_ticktof = [int(tof[x]) for x in tickpt]

ax_tr.imshow(bigdextr,aspect="auto")
#ax_tr.set_yticks(tickpt)
ax_tr.set_ylim([400,0])
#ax_tr.set_yticklabels(TR_ticktof)
ax_tr.set_ylabel("Transmission\nToF ($\mu$s)")
ax_tr.set_xticks([])

ax_pe.imshow(bigdexpe,aspect="auto")
ax_pe.set_ylim([400,0])
ax_pe.set_ylabel("Reflection\nToF ($\mu$s)")
ax_pe.set_xticks([])

showme(dpi=150)
clf()