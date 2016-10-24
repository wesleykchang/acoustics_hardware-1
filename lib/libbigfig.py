from pithy import *
from MTI_Tools import *
import pickle
import matplotlib.gridspec as gridspec
import os
import simplejson as json
import scipy.signal as sci
from urllib import urlopen as uo
from StringIO import StringIO as SI
import pandas as pd

####TODO STILL:
#### - add "memoization" so files are not reread every time
#### - range control
#### - add lines indicating beginning and end of cycles from current data
#### - make all data args optional, drawing from self.whatever by default
#### - SIUI integration, I guess
#### - ???

drop_pre = "/Users/j125mini/EASI/data/"

class BigFig():
    """ You may call this with either or both of iv data and acoustic 
    data. The iv data should be a single file, probably nda (but csv and will
    also work). The acoustic data should be a file template of the form:
        
        directory/cell_description
        
    That describes a series of files (one for each wave) of the form:
    
        directory/cell_description_channel_(PE or TR)_unixtime.json
        
    An real example is: 
        
        epoch_runs2/20150406_NMC18650_cell3_C_2_5_muxedup_rnd3_2_PE_1429752035.json
        
    (Technically, the code will search for your_template*PE*.json and 
    your_template*TR*.json to get PE and TR data, and then extract the 
    unixtime from the template. So those things, at least must always be 
    in the same place.)
    
    If either iv or acoustic is missing, it will simply be removed from 
    the plot and the other will take up more space. After instantiating,
    you can call genBigFig to plot the result:
        
        b = BigFig(iv=my/iv/file.nda, acoustic=my/acoustic/file)
        b.genBigFig()
        
    Optionally, you may pass a "skips" list to genBigFig to forcibly remove
    certain plots from the output. This would be identical to those data or
    files not being found, and can be useful for, say, if you have PE data
    but have no interest in showing it. An example would be:
    
        b.genBigFig(skips=["pe"])
    
    And your choices are:
    
        "cur" - Current (A) from iv data
        "pot" - Potential (V) from iv data
        "int" - Integral/Intensity from acoustic data
        "tr"  - transmission (TR) from acoustic data
        "pe"  - echo/reflection (PE) from acoustic data
    
    If tr or pe are skipped they will not be shown in the intensity plot
    either, even if the intensity plot is still displayed. :)
    
    If you want to run it continuously as new data is arriving, call refresh()
    in your loop:
    
        b = BigFig(iv=...,acoustic=...)
        b.genBigFig()
        
        while True:
            b.refresh()
            b.genBigFig()
            time.sleep(1)
        
    Note that, currently, refreshing completely rechecks everything, and
    so it takes a few seconds.
    
    SIUI data currently doesn't work. If you find any bugs or have ideas
    for improvement, please add it to the TODO STILL list up at the top
    of the file, or just code them yourself. :)
    """
    def __init__(self,iv=None,acoustic=None):
        
        if iv is None and acoustic is None:
            print "No datafiles given. Exiting 'gracefully'."
            sys.exit()
        
        #all iv data is in self.iv with keys ['time','potential','current']
        if iv is not None:
            self.iv_fn = iv
            self.iv = self.prepIV()
        else:
            self.iv_fn = None
            self.iv=None
            
        #all acoustic data is in self.acoustic with keys ['pe','tr'],
        # which both contain a dict with keys ['time','end','wave','int'].
        #  'time' is an array of the times of each wave, starting at 0s
        #  'end' is the last point (length) of the wave in microseconds
        #  'wave' contains the y-values of each wave, arbitrary units.
        #  'int' contains the absolute intensity/integral of the wave at that time.
        if acoustic is not None:
            self.acoustic_fn = acoustic
            self.acoustic = self.prepAcoustic()
        else:
            self.acoustic_fn = None
            self.acoustic={'pe':None,'tr':None}
        
        self.last_refresh = time.time()

        
#######################################################        
#                                                     #        
#                    PREPARE DATA                     #        
#                                                     #        
#######################################################        

    def refresh(self):
        now = time.time()
        if now-self.last_refresh<1:
            return
        if iv is not None:
            self.iv = self.prepIV()
            
        if acoustic is not None:
            self.acoustic = self.prepAcoustic()
        
        self.last_refresh = now

    def prepIV(self):
        if   self.iv_fn.find(".nda") > -1:
            return self._prepIVnda()
        elif self.iv_fn.find(".csv") > -1:
            return self._prepIVcsv()
        elif self.iv_fn.find(".res") > -1:
            return self._prepIVres()
    
    def _prepIVnda(self):
        raw = mti_data(drop_pre+self.iv_fn)
        data = {}
        for x in ['time','potential','current']:
            data[x] = raw[x]
        return data
        
    #TODO: auto-find arbin data. Leaving as-is for now because I don't have
    #any arbin data to play with
    def _prepIVcsv(self,arbin=False):
        file = drop_pre + self.iv_fn
        if arbin:
            data = genfromtxt(b1,delimiter=",",skip_header=1,usecols=(0,1,6,7)) 
            tim = (data[:,1]-data[:,1][0])/3600.0
            pot = data[:,3]
            cur = data[:,2]
        else: #don't understand why this uses uo but not fucking with it
            splits = uo(file).read().split("\n")
            header = splits.pop(0)
            cols = header.split(",")
            for i in splits:
                try:
                    p = i.split(",")
                    tim.append(float(p[26]))
                    pot.append(float(p[11]))
                    cur.append(float(p[12]))
                except:
                    pass #eeeeeeeh?
        data = {}
        data['time'] = tim
        data['potential'] = pot
        data['current'] = cur
        
        return data
    
    def _prepIVres(self):
        filename = drop_pre + self.iv
        raw = go("mdb-export "+filename+" Channel_Normal_Table")
        df = pd.read_csv(SI(data))
        df = df.sort(['Test_Time'])
        data = {}
        data['time'] = array(df['Test_Time']/3600.0)
        data['potential'] = array(df['Voltage'])
        data['current'] = array(df['Current'])
        return data
    
    #TODO: This don't work good. Make work better.
    def findCycles(self,data):
        """Feed this some prepped IV data to separate charge/discharge.
        Returns a dict of time,char,dis where char and dis contain indices
        of charging or discharging points."""
        t = []
        char_t = []
        dis_t = []
        fails = []
        for i in range(1,len(data['time'])):
            c0 = data['current'][i]
            c1 = data['current'][i-1]
            if abs(c0-c1) > .05:
                t.append(data['time'][i])
                if   c0 > 0:
                    char_t.append(len(t)-1)
                elif c0 < 0:
                    dis_t.append(len(t)-1)
            else: fails.append(data['time'][i])
        print fails
        t.append(max(data['time']))
        return {'time':t, 'char':char_t, 'dis':dis_t}
    
    def prepAcoustic(self):
        PEnames = sorted(glob(drop_pre+self.acoustic_fn+"*PE*.json"))
        TRnames = sorted(glob(drop_pre+self.acoustic_fn+"*TR*.json"))
        out = {'pe':None,'tr':None}
        if PEnames!=[]:
            out['pe']=self._prepEpoch(PEnames)
        if TRnames!=[]:
            out['tr']=self._prepEpoch(TRnames)
        return out
    
    def _prepEpoch(self,filenames):
        time,end,wave,intensity = self._prepEpochWaveform(filenames[0])
        data = {}
        data['time']=[time]
        data['end']=end
        data['wave']=[wave]
        data['int']=[intensity]
        for f in filenames[1:]:
            time,times,wave,intensity = self._prepEpochWaveform(f)
            if len(wave)==495 and intensity != 0:
                data['time'].append(time)
                data['wave'].append(wave)
                data['int'].append(intensity)
        data['time']=array(data['time'])-data['time'][0]#start at 0
        data['wave']=array(data['wave'])
        data['int']=array(data['int'])
        return data
    
    def _prepEpochWaveform(self,fil):
        wave = []
        time = -1
        end = -1
        try:
            if os.path.getsize(fil) > 30:
                f = json.load(open(fil))
                #"amplitudes"
                wave = list(abs(array(f['amp'])-127)-1)
                #time in seconds when the wave was taken
                time = int(fil.split('_')[-1].replace('.json',''))
                #time in microseconds between each amp
                end = f['time (us)'][-1]
        except:
            print "file too small: ", fil
            return 
        intensity = sum(wave)
        return time,end,wave,intensity
    
    def _prepSIUI(self):
        pass
            

#######################################################        
#                                                     #        
#               PREPARE AXES AND PLOTS                #        
#                                                     #        
#######################################################        

    def genBigFig(self,skips=[]):
        if skips.count('pot')==0 and self.iv is None:
            skips.append('pot')
        if skips.count('cur')==0 and self.iv is None:
            skips.append('cur')
            
        if (skips.count('int')==0 and 
            skips.count('pe')!=0 and skips.count('tr')!=0):
                skips.append('int')
        
        if skips.count('pe')==0 and self.acoustic['pe']['time']==[]:
            skips.append('pe')
        if skips.count('tr')==0 and self.acoustic['tr']['time']==[]:
            skips.append('tr')
            
        axes = self.genAxes(skips)
        ks = axes.keys()
                
        if ks.count('int')>0:
            self.setupIntensityPlot(axes['int'],skips)
        if ks.count('pe')>0:
            self.setupPEPlot(axes['pe'],skips)
        if ks.count('tr')>0:
            self.setupTRPlot(axes['tr'],skips)
        if ks.count('pot')>0:
            self.setupPotential(axes['pot'],skips)
        if ks.count('cur')>0:
            self.setupCurrent(axes['cur'],skips)
        
        #find the bottom and display the label. make other xticks=[]
        found_it = False
        for a in ['cur','pot','int','tr','pe']:
            if not found_it and ks.count(a)>0: 
                found_it = True
                self.setXLabel(axes[a])
            elif ks.count(a)>0:
                axes[a].set_xticks([])
            
        showme(kind="bigfig")
        clf()
        
    def genAxes(self,skips=[],size=(14,12)):
    
        #numbers in inches (w,h)
        fig       = figure(figsize=size)
        
        #number of base Specs we need, (rows,cols) (think frames)
        numSpecs = 0
        if skips.count('pe')==0:
            numSpecs = numSpecs+1
        if skips.count('tr')==0:
            numSpecs = numSpecs+1
        if skips.count('pot')==0 or skips.count('cur')==0 or numSpecs>0:
            numSpecs = numSpecs+1
        gss = gridspec.GridSpec(numSpecs, 1)
        
        #(rows,cols,gs) #s are arbitrary segments for use in plt.subplot
        gs = [] #these are Specs, again, think of them like frames
        for i in range(numSpecs):
            gs.append(gridspec.GridSpecFromSubplotSpec(4,1,gss[i]))
            
        #axes, range of segments in the gs.
        axes = {}
        gs_i = 0
        #show PE data?
        if skips.count('pe')==0:
            ax_pe      = plt.subplot(gs[gs_i][00:07,0])
            axes['pe'] = ax_pe
            gs_i       += 1
        #show TR data?
        if skips.count('tr')==0:
            ax_tr      = plt.subplot(gs[gs_i][00:07,0])
            axes['tr'] = ax_tr
            gs_i       += 1
        #PE,TR done#
        
        #should we show int, and what size?
        if skips.count('int')==0:
            if (skips.count('cur')==0 or 
                skips.count('pot')==0):
                 #yes iv (do below), yes int
                ax_int      = plt.subplot(gs[gs_i][0:2,0])
                axes['int'] = ax_int
            else: #no iv
                ax_int      = plt.subplot(gs[gs_i][0:4,0])
                axes['int'] = ax_int
        #int done#
            
        #show iv?
        if skips.count('int')==0:
            if skips.count('pot')==0:    
                if skips.count('cur')==0:
                    #yes pot, yes cur, yes int
                    ax_pot      = plt.subplot(gs[gs_i][2:3,0])
                    ax_cur      = plt.subplot(gs[gs_i][3:4,0])
                    axes['pot'] = ax_pot
                    axes['cur'] = ax_cur
                else: #yes pot, no cur, yes int
                    ax_pot      = plt.subplot(gs[gs_i][2:4,0])
                    axes['pot'] = ax_pot
            else:
                if skips.count('cur')==0:
                    #no pot, yes cur, yes int
                    ax_cur      = plt.subplot(gs[gs_i][2:4,0])
                    axes['cur'] = ax_cur
        else:
            if skips.count('pot')==0:    
                if skips.count('cur')==0:
                    #yes pot, yes cur, no int
                    ax_pot      = plt.subplot(gs[gs_i][0:2,0])
                    ax_cur      = plt.subplot(gs[gs_i][2:4,0])
                    axes['pot'] = ax_pot
                    axes['cur'] = ax_cur
                else: #yes pot, no cur, no int
                    ax_pot      = plt.subplot(gs[gs_i][0:4,0])
                    axes['pot'] = ax_pot
            else:
                if skips.count('cur')==0:
                    #no pot, yes cur, no int
                    ax_cur      = plt.subplot(gs[gs_i][0:4,0])
                    axes['cur'] = ax_cur
        #iv done#
        
        #make the defined axes fit in the given fig size
        gss.tight_layout(fig,h_pad=0.2)
        
        return axes
        
    def setupIntensityPlot(self,ax_int,skips=[]):
        if skips.count('int')==0:
            if skips.count('pe')==0:
                PEs = self.acoustic['pe']
                ax_int.plot(PEs['time']/3600.0,(PEs['int']-min(PEs['int']))/(max(PEs['int'])-min(PEs['int']))+1,'r',label="Reflected Signal")
                ax_int.annotate("Reflected Signal",xy=(1,1.8),color="r")
                ax_int.set_ylabel("Normalized Signal\n Amplitude (AU)")
                ax_int.set_xlim([0,max(PEs['time']/3600.0)])
                ax_int.set_ylim([-0.1,2.1])
                ax_int.set_yticks([])
            
            if skips.count('tr')==0:
                TRs = self.acoustic['tr']
                ax_int.plot(TRs['time']/3600.0,(TRs['int']-min(TRs['int']))/(max(TRs['int'])-min(TRs['int'])),'g',label="Transmitted Signal")
                ax_int.annotate("Transmitted Signal",xy=(1,0.3),color="g")
                ax_int.set_ylim([-0.1,2.1])
                ax_int.set_yticks([])
                ax_int.set_ylabel("Normalized Signal\n Amplitude (AU)")
                ax_int.set_xlim([0,max(TRs['time']/3600.0)])
                

    #TODO: automate clim
    def setupPEPlot(self,ax_pe,skips=[]):
        if skips.count('pe')==0:
            PEs = self.acoustic['pe']
            #no need to convert time units for spaceWaveforms
            imarray = self.spaceWaveforms(PEs['time'],PEs['wave'])
            pe_img = ax_pe.imshow(imarray.transpose(),aspect='auto',cmap=cm.jet)
            ax_pe.set_ylabel("Reflection\n Time of Flight ($\mu$s)")
            ax_pe.set_xticks([])
            self._genYTicks(ax_tr,PEs['end'],len(PEs['wave']))
            pe_img.set_clim([0,100])
            return pe_img

    #TODO: automate clim
    def setupTRPlot(self,ax_tr,skips=[]):
        if skips.count('tr')==0:
            TRs = self.acoustic['tr']
            #no need to convert time units for spaceWaveforms
            imarray = self.spaceWaveforms(TRs['time'],TRs['wave'])
            tr_img = ax_tr.imshow(imarray.transpose(),aspect='auto',cmap=cm.jet)
            ax_tr.set_ylabel("Transmission\n Time of Flight ($\mu$s)")
            ax_tr.set_xticks([])
            self._genYTicks(ax_tr,TRs['end'],len(TRs['wave']))
            tr_img.set_clim([0,100])
            return tr_img    
        
    def setupPotential(self,ax_pot,skips=[]):
        if skips.count('pot')==0:
            ax_pot.plot(self.iv['time'],self.iv['potential'],'k')
            ax_pot.set_yticks([min(self.iv['potential']),max(self.iv['potential'])])
            ax_pot.set_ylabel("Potential (V)")
            ax_pot.set_xlim(0,self.iv['time'][-1])
            ax_pot.set_ylim(min(self.iv['potential'])*0.9,max(self.iv['potential'])*1.1)
        
    def setupCurrent(self,ax_cur,skips=[]):
        if skips.count('cur')==0:
            ax_cur.plot(self.iv['time'],self.iv['current'],'k')
            ax_cur.set_ylabel("Current (A)")
            ax_cur.set_xlim(0,self.iv['time'][-1])
            if max(self.iv['current'])==0:
                ax_current.set_ylim(min(self.iv['current'])-0.5*abs(min(self.iv['current'])),abs(min(self.iv['current'])))
            else:
                ax_cur.set_ylim(min(self.iv['current'])-0.5*abs(min(self.iv['current'])),max(self.iv['current'])*1.5)
            ax_cur.set_yticks([min(self.iv['current']), max(self.iv['current'])])
            ax_cur.set_xlim(0,self.iv['time'][-1])
        
    def setXLabel(self,axis):
        axis.set_xlabel("Time (hr)")
        
    def _genYTicks(self,axis,end,length,num=None):
        if num is None:
            for i in [5,4,3]:
                if length%i==0:
                    num = i
                    break
        if num is None: #_still_ none
            num = 5
        ts = []
        for i in range(num):
            ts.append(i*length/num)
        ts.append(length)
        axis.set_yticks(ts)
        axis.set_yticklabels([int(x/float(ts[-1])*end) for x in ts])


#######################################################        
#                                                     #        
#                 UTILITY FUNCTIONS                   #        
#                                                     #        
#######################################################        
    
    def _median(self,data):
        counts = {}
        for i in data:
            try: counts[i]+=1
            except: counts[i]=1
        keys = counts.keys()
        try:
            m = keys[0]
            for k in keys[1:]:
                if counts[k]>counts[m]: m = k
            return m
        except:
            return 0

    def _interpolateWaveform(self,x,x0,x1,wave0,wave1):
        #y = y0+(y1-y0)*(x-x0)/(x1-x0). thanks wikipedia
        new = []
        w0 = wave0
        w1 = wave1
        for i in range(len(wave0)):
            new.append(w0[i]+(w1[i]-w0[i])*(x-x0)/(x1-x0))
        return new
        
    def _updateCSV(self):
        pass
    
    #TODO: also explain what this does, not just the thresh
    def spaceWaveforms(self,times,waves,interp_thresh=2,skip_thresh=4):
        """interp_thresh and skip_thresh determine how big of a jump between
        waveforms to interpolate and zero out, respectively, and are given
        as multiples of the median (aka how many waves are 'missing'+1). So
        skip_thresh=3 will place zeroed waves in empty space larger than 3 
        medians of normal space size."""
        spaces = [floor(times[i]-times[i-1]) for i in range(1,len(times))]
        mean = sum(spaces)/len(spaces)
        median = self._median(spaces)
        n_waves = [waves[0]]
        for i in range(1,len(times)-1):
            #gap too large; just replace missing waves with 0
            if   skip_thresh is not None and spaces[i] > skip_thresh*median:
                for j in range(1,int(spaces[i]/median)):
                    n_waves.append(array([0 for x in range(len(waves[0]))]))
            #interpolate missing waves
            elif interp_thresh is not None and spaces[i] > interp_thresh*median:
                for j in range(1,int(spaces[i]/median)):
                    w = self._interpolateWaveform(j, 0,
                                                  int(spaces[i]/mean),
                                                  waves[i-1], waves[i])
                    n_waves.append(w)
            else:
                n_waves.append(waves[i])
        n_waves.append(waves[-1])
        return array(n_waves)
    
if  False and __name__=="__main__":
    acoustic="epoch_runs2/20150406_NMC18650_cell3_C_2_5_muxedup_rnd3"
    iv="epoch_mti/data/20150422_212011_25_3.nda"
    
    bf = BigFig(iv=iv,acoustic=acoustic)
    bf.genBigFig()
        
    





























    