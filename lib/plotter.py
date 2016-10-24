from matplotlib import pyplot as plt
from glob import glob
import json, os
import numpy as np

# class Plotter():
#     def __init__(self,filepath):
#         self.filepath = filepath
#         self.metadatas = self.get_data_info()[u'data']
#         self.data = self.fetch_data()

#     def get_data_info(self):
#         fil = open(glob.glob(self.filepath+"/logfile.json")[0],"r").read()
#         return json.loads(fil)

#     def plot_cell(self,cellno):
#         serial = 'AppleWatchBatt_Cell' + cellno
#         ys = self.data[serial]
#         xs = [x*0.008 for x in range(len(ys))]
#         xlabel('Time(us)')
#         ylabel('Signal(V)')
#         plot(xs,ys)
#         showme()
#         clf()

def filler(ta,out):
    # ta is a list of the the times 
    # out is the bigdex
    out = out.T
    
    # get time between times and take average
    dta = np.diff(ta)
    avtime = np.mean(dta)
    
    #determine points in array where time is greater than the average slice by some fudge factors
    inserts = []
    for i in range(len(dta)):
        if dta[i] > 2.5*avtime: inserts.append([i,int(dta[i]/avtime)])
    
    #make the filler vector
    pad = np.zeros(len(out[0]))
    
    #make sub lists where there are breaks in data, and then make new list of pads
    outhold = []
    pads = []
    tc = [0]
    for i in inserts: 
        tc.append(i[0])
        pads.append([])
        for j in range(i[1]): pads[-1].append(pad)
    tc.append(len(out))
    for i in range(len(tc)-1): outhold.append(out[tc[i]:tc[i+1]])
    
    #put the stuff back together
    together = []
    for i in range(len(pads)):
        together = together + list(outhold[i])+list(pads[i])
    together = together + list(outhold[-1])
    
    out = np.array(together).T
    return out

if __name__ == "__main__":
    files = os.listdir('../Data/Sep_01_2016/TestID_140')
    files.remove('current.json')
    timelist = []
    yslist = []
    for timestamp in files:
        ys = json.load(open(os.path.join('../Data/Sep_01_2016/TestID_140',timestamp)))['amp']
        yslist.append(np.array(ys))
        time = float(timestamp.replace('_','.').rstrip('.json'))
        timelist.append(time)
    
    grid = filler(sorted(timelist),np.array(yslist))

    fig = plt.figure(figsize=(7,6))
    plt.imshow(grid,aspect='auto',interpolation="none")
    plt.ylabel("Time (us)")
    plt.xlabel("Freq (MHz)")
    plt.show()
    plt.clf()