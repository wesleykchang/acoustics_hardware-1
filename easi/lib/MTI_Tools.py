from pithy import *
from commands import getoutput as go
from glob import *
import os
import datetime
import sys
import mmap
from time import time as tizzy
import pandas

drop_pre = '/Users/j125mini/Downloads/TC5.4/_COM7/data/'

if len(sys.argv) < 2: pat = drop_pre+"MTI/*.nda"
else: pat = drop_pre+"MTI/"+sys.argv[1]
foo = glob(pat)


foo = sorted(glob(pat), key=os.path.getmtime)

#3/13
#Q seems to be something

#3/16/2013
#Q is the split.  Packet Length is 58 bytes. -> This is wrong, see 12/16/2013
#Potential = Int16 between bytes 23 and 25 (5*value/2^16)
#Current = Int 16 between bytes 26 and 28 (3 * value/2^16)
#Maybe Capacity as 2 bytes around byte 19 or 38? (plot vs. potential to get cap/V plots)
#Lookng for time as uint32 (long).  Maybe from
#Byte 7
#Byte 54
#MAybe capacity about byte 13 as uint16
#Bytes 18 and 19 are per step time.  they're hacked below to give better data

#3/28/2013
#Bytes 40 through 44 seem to be an accumulator for charge
#Bytes 47 through 51 seem to be an accumulator for energy

#5/2/2013
#Seeing through the fucking matrix
#Byte 17 is step type
#   4 = Rest
#   2 = CC_Dcharge
#   1 = CC_Charge
#   3 = CV_Charge

#6/20/2013
#Byte 13 is cycle #.  Does it go into 14?

#7/24/2013
#Byte 2128 aways begins a datetime (of the file starting) in the format "YY.MM.DD HH:MM:SS"

#12/16/2013
#There is no parsing variable: Q and R work sometimes but it's not deterministic.  
#We look for the first "FF" after location 2350, add 51 to that, and then split the remaining string into chunks of _59_. 
startfun = 2380

#12/22/2013
#adding a hack to determine the current capability of a unit
high_current_fudge_factor = 6.6
low_current_fudge_factor = 0.066

high_current_energy_factor = .02301/828372
low_current_energy_factor = .006424/23128153

high_current_capacity_factor = .01633/587882
low_current_capacity_factor = .001605234/5778841

current_guide = {}
current_guide['25'] = high_current_fudge_factor 
current_guide['06'] = low_current_fudge_factor
current_guide['09'] = low_current_fudge_factor
current_guide['07'] = high_current_fudge_factor 

energy_guide = {}
energy_guide['25'] = high_current_energy_factor 
energy_guide['06'] = low_current_energy_factor
energy_guide['09'] = low_current_energy_factor
energy_guide['07'] = high_current_energy_factor 

capacity_guide = {}
capacity_guide['25'] = high_current_capacity_factor 
capacity_guide['06'] = low_current_capacity_factor
capacity_guide['09'] = low_current_capacity_factor
capacity_guide['07'] = high_current_capacity_factor 

#Trying to figure out states for byte X, doesn't really work yet
guide = {
     4 : 0,
     2 : -1,
     1 : 1,
     3 : 1
        }

def mti_start_time(filer):
    foo = open(filer)
    foo.seek(2126)
    return foo.read(19)

def mti_name(filer):
    foo = open(filer)
    foo.seek(2145)
    foo = foo.read(150)
    out = ""
    for o in foo:
        if ord(o) > 30 and ord(o) < 128:
            out+=o
    return out

def mti_data(flier,debug = False):

    #Read in File
    dooer = os.open(flier,os.O_RDONLY)
    dooer = mmap.mmap(dooer,0, prot=mmap.PROT_READ)
 
    #Get Cycler Number, map to current range    
    cycler_code = flier.split("/")[-1].split("_")[2]
    try:
        current_factor = current_guide[cycler_code]
        energy_factor = energy_guide[cycler_code]
        capacity_factor = capacity_guide[cycler_code]
    except:
        current_factor = high_current_fudge_factor
        energy_factor = high_current_energy_factor
        capacity_factor = high_current_capacity_factor

    
    #This is how we split, it's ugly but it works
    #I heard you like hacks, so here's a hack to hack your hacks 
    location = dooer.find(chr(255)+chr(01),startfun)+51
    parseBit = dooer[location]
    things = []
    total = len(dooer)
    pl = 59 #packet length
    if debug: start = tizzy()
    
    while location < total:
        things.append(dooer[location:location+pl])
        location = location+pl

    if debug:
        print tizzy() - start
        start = tizzy()

    
    #Get Run Information
    dooer.seek(2145)
    fame = dooer.read(150)
    fame = "".join([x for x in fame if ord(x) < 128 and ord(x) >31])

    #Get Cycler # and Channel
    ps = flier.split("/")[-1].split(".")[0].split("_")
    channel = ps[2]+"_"+ps[3]

    #Now for the hard stuff
    volts = []
    curr = []
    ctime = []
    we = []
    f1 = []
    f2 = []
    f3 = []
    f4 = []
    cycles = 0
    first = True
    ff = 0
    holdit = 0
    count=0
    cycle = []
    bit = True

    if debug: start = tizzy()

    for t in things:
        if len(t) == pl and ord(t[8])< 255:
            #Get Potential
            #needs to be uint! (no negative potential)
            #3/9/2014 -> changed to int16 from uint16 because Ben and Jit say it can go negative.
            this = fromstring(t[23:25],dtype=uint16)[0] 
            volts.append(this)

            #Get Current
            #needs to be int16 (negative current)
            this = fromstring(t[27:29],dtype=int16)[0]
            curr.append(this)   
            
            #Get Time
            s = 18
            e = s+4
            this = fromstring(t[s:e],dtype=uint32)[0]
            this = this >> 8
            if len(we) >0:
                if (we[-1]) > (holdit+this): 
                    holdit = int(we[-1]) 
            we.append(holdit+this)
            ctime.append(this)
            count+=1
            
            #Get Cycles
            this = fromstring(t[13],dtype=uint8)[0]
            cycle.append(this)
            
            #SubStep
            f1.append(fromstring(t[16],dtype=uint8)[0])
            f2.append(fromstring(t[17],dtype=uint8)[0])
            
            #Get Capacity Passed (units unclear)
            s = 39 #I think this is capacity passed per step
            f3.append(capacity_factor*fromstring(t[s:s+4],dtype=uint32)[0])
            
            #Get Energy Passed (Units unclear)
            s = 47 #I think this is energy passed per step
            f4.append(energy_factor*fromstring(t[s:s+4],dtype=uint32)[0])
            
            
            
    if debug:
        print tizzy() - start
        start = tizzy()
    
    time = array(we)/(60*60.)
    ctime = array(ctime)/(60*60.)
    
    cycle_life = []
    foo = 1

    #steps in this cycle
    sic = 0

    for c in range(len(cycle)):
        sic = 0
        if c > 0:
            if cycle[c] != cycle[c-1]:
                foo = foo+1
        cycle_life.append(foo)
        sic += 1

    cycle = cycle_life
    if debug:
        print tizzy() - start
        start = tizzy()
    #sixteen bits @ a maximum of 6.55 V (apparently)
    potential = array(volts)*6.55/(2**16)
    
    #sixteen bits @ a maximum of marked cycler -> current factor is a fudge factor, see notes above
    current = array(curr).T*current_factor/(2**16) 
    if debug:
        print tizzy() - start
        start = tizzy()
        print len(time)
    return {'time':time,'ctime':ctime,'potential':potential,'current':current,'cycle':cycle,'step_type':f2,'sub_step':f1,'capacity_passed':f3,'energy_passed':f4,'name':fame,'channel':channel}

def mti_cycle_analysis(dd):
    cycle_count = int(amax(dd['cycle']))
    out= {}
    out['ce'] =zeros(cycle_count)
    out['de'] =zeros(cycle_count)
    out['cc'] =zeros(cycle_count)
    out['dc'] =zeros(cycle_count)

    for i in range(len(dd['time'])):
        if i > 0:
            if dd['capacity_passed'][i] == 0.0 and dd['capacity_passed'][i-1] > dd['capacity_passed'][i] and dd['cycle'][i] == dd['cycle'][i-1]:
                if dd['current'][i-1] < 0 :
                    out['de'][dd['cycle'][i-1]-1] +=  dd['energy_passed'][i-1]
                    out['dc'][dd['cycle'][i-1]-1] +=  dd['capacity_passed'][i-1]
                else:
                    out['ce'][dd['cycle'][i-1]-1] +=  dd['energy_passed'][i-1]
                    out['cc'][dd['cycle'][i-1]-1] +=  dd['capacity_passed'][i-1]
        elif i == len(dd['time']) - 1:
                if dd['current'][i-1] < 0 :
                    out['de'][dd['cycle'][i-1]-1] +=  dd['energy_passed'][i-1]
                    out['dc'][dd['cycle'][i-1]-1] +=  dd['capacity_passed'][i-1]
                else:
                    out['ce'][dd['cycle'][i-1]-1] +=  dd['energy_passed'][i-1]
                    out['cc'][dd['cycle'][i-1]-1] +=  dd['capacity_passed'][i-1]
            
                    

    return out

def mti_update_time(filer):
    return datetime.datetime.isoformat(datetime.datetime.fromtimestamp(os.path.getmtime(ftg)))

def mti_last_time(filename):
    filename = filename.split("/")[-1]
    parts = filename.split("_")
    year = int(parts[0][0:4])
    month = int(parts[0][4:6])
    day = int(parts[0][6:8])
    hour = int(parts[1][0:2])
    mins = int(parts[1][2:4])
    sec = int(parts[1][4:6])
    foo = datetime.datetime(year, month, day, hour, mins, sec, 0)
    return foo

def lastspark(l):
    fil = l.split("/")[-1]
    width = 5
    out = {}
    ls = {}
    out['spark']=fil
    try:
        csv = drop_pre+"/MTI_CSV_drop/"+fil.replace(".nda","_pct.csv")
        pd =  pandas.read_csv(csv)
        
        #this could probaby be neater
        c =   pd['Cycle'].iget(-1) - 1
        lp =  pd['Potential(V)'].iget(-1)
        lc =  pd['Current(A)'].iget(-1)
        lcc = pd['CapacityPassed(Ahr)'].iget(-1)
        lce = pd['EnergyPassed(Whr)'].iget(-1)
        a = rcParams['figure.figsize']
        holdit = a
        #rcParams['figure.figsize'] = [width,1]
        figure(figsize=(width, 1))
        for i in range(5,-1,-1):
            plot(pd['Potential(V)'][pd['Cycle']==c-i],linewidth=1,color=(.2*i,.2*i,.2*i))
        
        plot(pd['Potential(V)'][pd['Cycle']==c+1],linewidth=2,color='red')
        xticks([])
        yticks([])
        axis('off')
        tim = str(int(time.time()))
        tip = ".svg"
        image = drop_pre+'MTI_sparks/'+l.replace(".nda",tip)
        himage = "http://steingart.princeton.edu:8002/static/realfiles/MTI_sparks/"+l.replace(".nda",tip)
        savefig(image)
        clf()
        close('all')
        rcParams['figure.figsize'] = a
        we_out = str(int(100*width/3.0))
        
        ok = '<img style="width:'+we_out+'px;vertical-align:middle;" src="'+himage+'">'
        out['spark']=ok
        oof = {}
        oof['Cycle']         = str(int(c)+1)
        oof['Potential (V)']     = str(round(lp,2))
        if lc == 0:
            oof['State'] = "OCV"
            oof['Current (A)'] = 0

        elif lc > 0:
            oof['State'] = "Charge"
            oof['Charge Passed (Ahr)'] = str(round(lcc,4))
            oof['Current (A)']       = str(round(lc,4))
            oof['Energy Passed (Whr)'] = str(round(lce,4))
        else:
            oof['State'] = "Discharge"
            oof['Charge Passed (Ahr)'] = str(round(lcc,4))
            oof['Current (A)']       = str(round(lc,4))
            oof['Energy Passed (Whr)'] = str(round(lce,4))
        
        out['lasts'] = oof
        return out

    except Exception as err:
        print 'lastpark:',err
        return out
    
if __name__=="__main__": 
    print "looks like it worked"
    #boob = drop_pre+"MTI/20131018_145509_07_6.nda"
    boob = drop_pre+"MTI/20140507_163340_06_7.nda" # -> doesn't work
    #boob = drop_pre+"MTI/20130322_184202_25_4.nda" -> works
    foo = mti_data(boob,debug=True)
    plot(foo['time'])
    showme()
    clf()
    print lastspark("20140507_163340_06_7.nda")
