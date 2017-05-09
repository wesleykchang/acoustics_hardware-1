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
    max_samples = 32768
    sample_rate = max_samples/sweep_t
    k = (stop_f-start_f)/sweep_t
    if sample_rate <= 10*stop_f:
        print("Warning: Sample rate below 10x! Sample rate: %f 10x: %f" %(sample_rate,10*stop_f))
    t = np.linspace(0,sweep_t,max_samples)
    chirp = np.sin(2*np.pi*(start_f*t + (k/2)*t**2))
    return chirp,sample_rate



if __name__ == '__main__':
    filename = 'table_state.json'
    if not os.path.exists(filename):
        filename = '../table_state.json'
    if not os.path.exists(filename):
        raise FileNotFoundError('table_state.json not found')

    macAddress = '9005'
    serialnumber = sys.argv[1]
    start_f = float(sys.argv[2])
    stop_f = float(sys.argv[3])
    sweep_t = float(sys.argv[4])
    num_freqs = int(sweep_t/(1/start_f))
    sample_rate = 3*stop_f

    num_sweeps = 1



    inc = (stop_f - start_f)/num_freqs
    dwelltime = sweep_t/num_freqs

    # channel1 = '0,7'
    # channel2 = '6,7'

    last_tid = getTestID(filename)
    new_tid = last_tid + 1
    new_tid = '_'.join((macAddress, str(new_tid)))
    dtformat = '%b %d %Y %H:%M:%S'
    dateformat = '%Y_%m_%d'
    dt = datetime.datetime.now()

    row = {
        "date_fname":dt.strftime(dateformat),
        "startdate":dt.strftime(dtformat),
        "testid":new_tid,
        "lastwaveform":"",
        "project":"resonance2",
        "serialnumber":serialnumber,
        "mode(tr/pe)":"tr",
        "channel":"55,55",
        "channel2":"55,55",
        "gain(db)":"20",
        "delay(us)":"0",
        "time(us)":"40",
        "freq(mhz)":"0",
        "filtermode":"0",
        "cyclercode":"",
        "notes":"",
        "run(y/n)":"y",
        "singleshot":"false",
        "start_f" : start_f,
        "stop_f" : stop_f,
        "sweep_t" : sweep_t,
        "num_freqs" : num_freqs
    }

    ps = Picoscope(avg_num=0, resonance=True, duration = sweep_t,maxV=2,sample_rate=sample_rate)
    s = Saver()
    try:
        for i in range(num_sweeps):
            if len(sys.argv) == 6 and sys.argv[5]== 'arb':
                ys, sample_rate = linear_chirp(start_f,stop_f,sweep_t)
                w_data = ps.generate_waveform(ys, sweep_t)
            else:
                w_data = ps.signal_generator(frequency=start_f, stopFreq=stop_f, shots=0, numSweeps=1, increment=inc, dwellTime=dwelltime)
            ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
            w = data.Wave(framerate=sample_rate, amps=w_data[1])
            w_s = w.to_spectrum()
            if i == 0:
                # print(w_data[1])
                wavesum = w_data[1]
                specsum = np.array(w_s.hs)
            else:
                wavesum = wavesum + w_data[1]
                specsum = np.add(specsum,np.array(w_s.hs))
            # time.sleep(2.5) #give the power amp a chance to stabilize between tests
        wave_avgs = wavesum/num_sweeps
        wav = data.Wave(amps = wave_avgs, framerate = sample_rate)
        wav.plot(scale_x=False)
        plt.show()
        plt.clf()

        spec = wav.to_spectrum()
        spec.plot()
        plt.title("avg1")
        plt.show()
        plt.clf()

        # spec_avgs = specsum/num_sweeps
        # print(spec_avgs)
        # sp = data.Spectrum(spec_avgs,sample_rate)
        # sp.plot()
        # plt.show()
        incTable(filename)
        s.saveData(w_data,row,None)
    except:
        incTable(filename)
        import traceback
        print(traceback.format_exc())

