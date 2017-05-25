'''
This script was used in the first KT DOE project, experiment 2: couplant
It takes 10 waveform measurements with a 30 second pause between each

First command line argument: last 4 digits of MAC address for host computer
Second command line argument: serialnumber for test
Third command line argument: channel1
Fourth command line argument: channel2

ex:
python3 KT_Couplant_DOE.py 9005 serialnumber 0,7 6,7

'''
import sys
import json
import os
import datetime
import time
sys.path.append('lib')
import utils
sys.path.append('../EASI-analysis/analysis')
from filesystem import Saver
import data
from libPicoscope import Picoscope
import numpy as np
import time
import json
from scipy.optimize import fsolve

from matplotlib import pyplot as plt

def getTestID(filename):

    with open(filename) as f:
        table_state = json.load(f)

    last_tid = int(table_state['last_tid'])
    return last_tid


def incTable(filename):

    with open(filename) as f:
        table_state = json.load(f)

    last_tid = int(table_state['last_tid'])
    new_tid = last_tid+1
    table_state['last_tid'] = new_tid
    with open(filename, 'w') as f:
        json.dump(table_state, f)

def linear_chirp(start_f,stop_f,sweep_t):
    """Creates a linear chirp, intended for single sweeps, therefore very limited in terms of 
    sweep duration/sample rate"""
    max_samples = 32768
    sample_rate = max_samples/sweep_t
    k = (stop_f-start_f)/sweep_t
    if sample_rate <= 10*stop_f:
        print("Warning: Sample rate below 10x! Sample rate: %f 10x: %f" %(sample_rate,10*stop_f))
    t = np.linspace(0,sweep_t,max_samples)
    chirp = np.sin(2*np.pi*(start_f*t + (k/2)*t**2))
    return chirp,sample_rate

def segments(start_f,stop_f,sweep_t,sample_factor=10):
    """Takes a sweep range and duration, and splits it into multiple smaller sweeps based on
    equipment buffer and the sample factor (e.g. always keep sampling frequency to be ~10f. Does
    this based off of a linear approximation. Returns list of times and y values for each segment"""
    max_samples = 32768
    k = (stop_f-start_f)/sweep_t #how quickly the chirp increases
    t_total = 0
    chirp_list = []
    t_list = []

    i = 0 #index for how many loops. used to increase samples

    while t_total < sweep_t:
        i += 1
        func = lambda t : sample_factor*k*t**2 + sample_factor*start_f*t - max_samples*i
        t_i = fsolve(func,1)[0] - t_total
        if (t_total+t_i) > sweep_t:
            sweep_end = sweep_t
        else:
            sweep_end = t_total + t_i
        t_array = np.linspace(t_total,sweep_end, max_samples)
        chirp_i = np.sin(2*np.pi*(start_f*t_array + (k/2)*t_array**2))

        t_list.append((t_total,sweep_end,(sweep_end-t_total))) #tuple containing start, end, duration
        chirp_list.append(chirp_i)
        t_total += t_i

    return t_list, chirp_list, k

def save_res_data(spec_obj, row):
    data = {}
    data['framerate'] = spec_obj.framerate
    data['hs'] = list(spec_obj.hs.view(float))
    data.update(row)

    folder = '../Resonance'
    if os.path.exists(folder) == False:
        os.mkdir(folder)
    filename = os.path.join(folder, row['serialnumber'])
    json.dump(data, open(filename, 'w'))
    return

def average_specs(spec_list):
    '''
    averages together all of the waves in the waveset. returns a wave object
    '''
    avg = []
    for spec in spec_list:
        avg.append(np.abs(spec.hs))
    ref = sorted(spec_list)[0]

    avg = np.mean(np.transpose(avg),axis=1)
    s = data.Spectrum(hs, spec_list[0].framerate)
    return s


class Resonator():
    def __init__(self,start_f,stop_f,sweep_t,arb=False):
        self.start_f = start_f
        self.stop_f = stop_f
        self.sweep_t = sweep_t
        self.ps = Picoscope(avg_num=0, resonance=True, duration = sweep_t,maxV=.02,sample_rate=sample_rate) ###Change this to be dynamic!!
        self.arb =arb

        self.num_freqs = int(sweep_t/(1/start_f))
        self.sample_rate = 3*stop_f
        self.num_sweeps = 1


    def get_single_generator(self):
        w_data = ps.signal_generator(frequency=start_f, stopFreq=stop_f, shots=0, numSweeps=1, increment=inc, dwellTime=dwelltime)
        ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
        w = data.Wave(framerate=sample_rate, amps=w_data[1])
        w_s = w.to_spectrum()
        return [w,w_s]

    def get_single_arb(self):
        t_list, chirp_list, k = segments(self.start_f,self.stop_f,self.sweep_t)
        i = 0
        w_data = np.array([])
        total_ts = np.array([])
        for time in t_list:
            print(time)
            rx_data = ps.generate_waveform(chirp_list[i], time[2],rx_sample_rate)
            sample_ts = np.linspace(time[0],time[1],len(rx_data[1]))
            #add chirp segment to total time data
            w_data = np.append(w_data,rx_data[1])
            total_ts = np.append(total_ts, sample_ts)
            seg_wave = data.Wave(amps=rx_data[1],framerate=rx_sample_rate,delay=time[0])
            f0_i = (self.start_f + time[0] * k) #f at beginning of chirp segment
            f1_i = (self.start_f + time[1] * k) #f at end of chirp seg
            thresh = 0
            # thresh = start_f/20 #arbitrary threshold for filter limits
            seg_spec = seg_wave.to_spectrum()
            seg_spec.band_stop(f0_i - thresh, f1_i + thresh)
            if i == 0:
                seg_total = seg_spec
            else:
                seg_total += seg_spec
            i += 1
        return [data.Wave(w_data,framerate=self.sample_rate), seg_total]

    def get_data(self,plot=False,save = None):
        spec_list = []
        for i in num_sweeps:
            if self.arb:
                wav,spec = get_single_arb()
            else:
                wav,spec = get_single_generator()
            spec_list.append(spec)
        avg_s = average_specs(spec_list)

        if plot:
            wav.plot()
            plt.show()

            avg_s.plot()
            plt.show()
        return avg_s


    def loop(self):
        pass




if __name__ == '__main__':
    serialnumber = sys.argv[1]
    start_f = float(sys.argv[2])
    stop_f = float(sys.argv[3])
    sweep_t = float(sys.argv[4])
    num_freqs = int(sweep_t/(1/start_f))
    num_sweeps = 1
    sample_rate = 3*stop_f

    inc = (stop_f - start_f)/num_freqs
    dwelltime = sweep_t/num_freqs

    row = {
        "startdate":dt.strftime(dtformat),
        "project":"resonance3",
        "serialnumber":serialnumber,
        "start_f" : start_f,
        "stop_f" : stop_f,
        "sweep_t" : sweep_t,
        "num_freqs" : num_freqs
    }

    r = Resonator(start_f,stop_f,sweep_t)
    r.get_data(plot=True)

