'''
First command line argument: Name of the test
Second command line argument: start frequency (Hz)
Third command line argument: end frequency (Hz)
Fourth command line argument: sweep duration (s)
Fifth command line argument(optional): 

ex:


'''
import sys
import json
import os
import datetime as dt
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


def save_res_data(spec_obj, row):
    dat = {}
    dat['framerate'] = spec_obj.framerate
    dat['hs'] = list(spec_obj.hs.view(float))
    dat.update(row)

    folder = '../Resonance'
    if os.path.exists(folder) == False:
        os.mkdir(folder)
    filename = os.path.join(folder, row['serialnumber'])
    json.dump(dat, open(filename, 'w'))
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
    s = data.Spectrum(avg, spec_list[0].framerate)
    return s

def save_res_spec(spec_obj, fname, folder_name):
    """Saves the resonance spectra and a timestamp.
    spec_obj: Spectrum object to be saved
    fname: name of file
    folder_name: name of folder
    """
    dat = {}
    dat['framerate'] = spec_obj.framerate
    dat['hs'] = list(spec_obj.hs.view(float))
    dat['timestamp'] = time.time()

    folder = os.path.join('../Resonance',folder_name)
    if os.path.exists(folder) == False:
        os.makedirs(folder)
    filename = os.path.join(folder, fname)
    json.dump(dat, open(filename, 'w'))
    return


def pad(array, pad_no):
    """Pads an array. useful for averaging spectra with different framerates"""
    zs = np.zeros(pad_no)
    padded = np.append(array,zs)
    return padded


class Resonator():
    """Class for collecting resonance data.

    start_f: frequency at the start of the sweep
    stop_f: frequency at the end of the sweep
    sweep_t: duration of the sweep
    arb: optional argument to use the AWG instead of the function generator,
    which it defaults to.
    test_name: optional argument to name the test. used to determine folder location
    """
    def __init__(self,start_f,stop_f,sweep_t,arb=False,test_name = "resonance_test"):
        self.start_f = start_f
        self.stop_f = stop_f
        self.sweep_t = sweep_t
        self.ps = Picoscope(avg_num=0, resonance=True, duration = sweep_t,maxV=.2,sample_rate=sample_rate) ###Change this to be dynamic!!
        self.arb =arb

        self.num_freqs = int(sweep_t/(1/start_f)) #number of frequencies for function generator. Makes sure there is at least one cycle for each.
        self.sample_rate = 3*stop_f #adjusting this can sometimes speed up the FFT

        self.num_sweeps = 1 #number of times to sweep when averaging


    def get_single_generator(self):
        """Gets a single waveform using the built-in function generator. Returns both a wave object
        and a spectrum object"""
        w_data = self.ps.signal_generator(frequency=self.start_f, stopFreq=self.stop_f, shots=0, numSweeps=1, increment=inc, dwellTime=dwelltime)
        self.ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
        w = data.Wave(framerate=sample_rate, amps=w_data[1])
        w_s = w.to_spectrum()
        return [w,w_s]

    def get_single_arb(self):
        """Gets a single waveform using the AWG. This takes a linear sweep equation, splits it into different 32k chunks and pulses each
        one before stitching together the resonance spectra. Returns both a wave object and a spectrum object"""
        t_list, chirp_list, k = self.segments()
        i = 0
        w_data = np.array([])
        total_ts = np.array([])
        for times in t_list:
            print(times)
            rx_data = self.ps.generate_waveform(chirp_list[i], times[2],self.sample_rate)
            sample_ts = np.linspace(times[0],times[1],len(rx_data[1]))
            #add chirp segment to total time data
            w_data = np.append(w_data,rx_data[1])
            total_ts = np.append(total_ts, sample_ts)
            if i == 0:
                pad_no = 0
            else:
                pad_no = (len(seg_total.hs)-1)*2 - len(rx_data[1])
            seg_wave = data.Wave(amps=pad(rx_data[1],pad_no),framerate=self.sample_rate,delay=times[0])
            f0_i = (start_f + times[0] * k) #f at beginning of chirp segment
            f1_i = (start_f + times[1] * k) #f at end of chirp seg
            print(f0_i,f1_i)
            thresh = stop_f*.1
            seg_spec = seg_wave.to_spectrum()
            seg_spec.band_pass(f0_i - thresh,f1_i + thresh)
            if i == 0:
                seg_total = seg_spec
            else:
                seg_total += seg_spec
            i += 1
            pad_no = len(seg_total.hs)
        self.ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
        return [data.Wave(w_data,framerate=self.sample_rate), seg_total]

    def linear_chirp(self):
        """Creates a linear chirp, intended for single sweeps, therefore very limited in terms of 
        sweep duration/sample rate"""
        max_samples = 32768
        sample_rate = max_samples/self.sweep_t
        k = (self.stop_f-self.start_f)/self.sweep_t
        if sample_rate <= 10*self.stop_f:
            print("Warning: Sample rate below 10x! Sample rate: %f 10x: %f" %(sample_rate,10*self.stop_f))
        t = np.linspace(0,self.sweep_t,max_samples)
        chirp = np.sin(2*np.pi*(self.start_f*t + (k/2)*t**2))
        return chirp,sample_rate

    def segments(self,sample_factor=10):
        """Takes a sweep range and duration, and splits it into multiple smaller sweeps based on
        equipment buffer and the sample factor (e.g. always keep sampling frequency to be ~10f. Does
        this based off of a linear approximation. Returns list of times and y values for each segment"""
        max_samples = 32768
        k = (self.stop_f-self.start_f)/self.sweep_t #how quickly the chirp increases
        t_total = 0
        chirp_list = []
        t_list = []

        i = 0 #index for how many loops. used to increase samples

        while t_total < self.sweep_t:
            i += 1
            func = lambda t : sample_factor*k*t**2 + sample_factor*self.start_f*t - max_samples*i
            t_i = fsolve(func,1)[0] - t_total
            if (t_total+t_i) > self.sweep_t:
                sweep_end = self.sweep_t
            else:
                sweep_end = t_total + t_i
            t_array = np.linspace(t_total,sweep_end, max_samples)
            chirp_i = np.sin(2*np.pi*(self.start_f*t_array + (k/2)*t_array**2))

            t_list.append((t_total,sweep_end,(sweep_end-t_total))) #tuple containing start, end, duration
            chirp_list.append(chirp_i)
            t_total += t_i

        return t_list, chirp_list, k

    def get_data(self,plot=False):
        """Will call either get_single_arb or get_single_generator based off of whether or not arb flag is enabled.
        Also implements averaging returns the averaged spectrum as a Spectrum object"""
        spec_list = []
        for i in range(num_sweeps):
            if self.arb:
                wav,spec = self.get_single_arb()
            else:
                wav,spec = self.get_single_generator()
            self.ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
            spec_list.append(spec)
        avg_s = average_specs(spec_list)

        if plot:
            wav.plot()
            plt.show()
            avg_s.plot()
            plt.show()
        return avg_s

    def loop(self,sleep_time,save=True):
        """Intermittently takes data in intervals of sleep_time (number of seconds). if save flag is enabled,
        will save the data in a folder called test_name"""
        #sleep_time is in seconds
        loop_index = 0
        sweep_index = 0
        while True:
            for i in range(3):
                s = self.get_data()
                filename = str(loop_index) + '_' + str(i)
                if save:
                    save_res_spec(s,filename,self.test_name)
                sweep_index += 1
            time.sleep(sleep_time)
            loop_index += 1


if __name__ == '__main__':
    testname = sys.argv[1]
    start_f = float(sys.argv[2])
    stop_f = float(sys.argv[3])
    sweep_t = float(sys.argv[4])
    num_freqs = int(sweep_t/(1/start_f))
    num_sweeps = 1
    sample_rate = 5*stop_f

    inc = (stop_f - start_f)/num_freqs
    dwelltime = sweep_t/num_freqs

    if len(sys.argv) == 6 and sys.argv[5]== 'arb':
        arb = True
    else:
        arb = False

r = Resonator(start_f,stop_f,sweep_t,arb,test_name=testname)
s = r.get_data()
s.plot()
plt.show()
# plt.xlim([1e3,90e3])
# plt.show()
# r.loop(300)
