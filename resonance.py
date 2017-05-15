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
    max_samples = 32768
    sample_rate = max_samples/sweep_t
    k = (stop_f-start_f)/sweep_t
    if sample_rate <= 10*stop_f:
        print("Warning: Sample rate below 10x! Sample rate: %f 10x: %f" %(sample_rate,10*stop_f))
    t = np.linspace(0,sweep_t,max_samples)
    chirp = np.sin(2*np.pi*(start_f*t + (k/2)*t**2))
    return chirp,sample_rate

def segments(start_f,stop_f,sweep_t,sample_factor=5):
    max_samples = 32768
    k = (stop_f-start_f)/sweep_t #how quickly the chirp increases
    t_total = 0
    chirp_list = []
    t_list = []
    # t_arrays = []

    i = 0 #index for how many loops. used to increase samples

    while t_total < sweep_t:
        i += 1
        func = lambda t : sample_factor*k*t**2 + sample_factor*start_f*t - max_samples*i
        t_i = fsolve(func,1)[0] - t_total
        if (t_total+t_i) > sweep_t:
            t_array = np.linspace(t_i,sweep_t,max_samples)
        else:
            t_array = np.linspace(t_total,t_total+t_i, max_samples)
        # t_arrays.append(t_array)
        chirp_i = np.sin(2*np.pi*(start_f*t_array + (k/2)*t_array**2))
        # plt.plot(t_array,chirp_i,'-')
        # plt.show()

        # print(max_samples/(t_i))
        # w = data.Wave(amps = chirp_i, delay=t_total, framerate = max_samples/(t_i))
        # print(w.framerate)
        # w.plot()
        # plt.show()

        # s = w.to_spectrum()
        # s.plot()
        # plt.show()


        t_list.append((t_total,t_total+t_i,t_i)) #tuple containing start, end, duration
        chirp_list.append(chirp_i)
        t_total += t_i

    return t_list, chirp_list





# def linear_chirp_chunked(start_f,stop_f,sweep_t):
#     max_samples = 32768
#     sample_rate = max_samples/sweep_t
#     k = (stop_f-start_f)/sweep_t
#     if sample_rate <= 10*stop_f:
#         print("Warning: Sample rate below 10x! Sample rate: %f 10x: %f" %(sample_rate,10*stop_f))
#     t = np.linspace(0,sweep_t,max_samples)
#     chirp = np.sin(2*np.pi*(start_f*t + (k/2)*t**2))
#     return chirp,sample_rate



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
    num_sweeps = 1
    sample_rate = 3*stop_f



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

    ps = Picoscope(avg_num=0, resonance=True, duration = sweep_t,maxV=2,sample_rate=sample_rate) ###Change this to be dynamic!!
    s = Saver()
    try:
        for i in range(num_sweeps):
            print(len(sys.argv),sys.argv[4])
            if len(sys.argv) == 6 and sys.argv[5]== 'arb':
                t_list, chirp_list = segments(start_f,stop_f,sweep_t)
                i = 0
                total_data = np.array([])
                total_ts = np.array([])
                for time in t_list:
                    print(time)
                    # ps.sample_rate = (32000/time[2])
                    w_data = ps.generate_waveform(chirp_list[i], time[2])
                    # ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
                    # ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
                    sample_ts = np.linspace(time[0],time[1],len(w_data[1]))
                    # plt.plot(sample_ts, w_data[1])
                    # plt.show()
                    total_data = np.append(total_data,w_data[1])
                    total_ts = np.append(total_ts, sample_ts)
                    i += 1

                    seg_wave = data.Wave(amps=w_data[1],framerate=sample_rate,delay=time[0])
                    seg_wave.plot(scale_x=False)
                    plt.show()

                    seg_spec = seg_wave.to_spectrum()
                    seg_spec.plot()
                    plt.show()
                print(total_ts)
                print(total_data)
                plt.plot(total_ts,total_data,'b-')
                plt.show()

            else:
                w_data = ps.signal_generator(frequency=start_f, stopFreq=stop_f, shots=0, numSweeps=1, increment=inc, dwellTime=dwelltime)
            ps.signal_generator(frequency=1e6, shots=1) #necessary for returning the picoscope to 0
            # w = data.Wave(framerate=sample_rate, amps=w_data[1])
            # w.plot(scale_x=False)
            # plt.show()
            # w_s = w.to_spectrum()
            # w_s.plot()
            # plt.show()
            # if i == 0:
            #     specsum = w_s
            # else:
            #     # wavesum = wavesum + w_data[1]
            #     specsum += w_s
            # time.sleep(2.5) #give the power amp a chance to stabilize between tests

        # specsum.hs = specsum.hs/num_sweeps
        # specsum.plot()

        # plt.title(serialnumber)
        # plt.show()
        # plt.clf()

        # incTable(filename)
        # s.saveData(w_data,row,None)

    except:
        import traceback
        print(traceback.format_exc())

    # avg_data = np.mean(mean_array,axis=0)
    # wav = data.wave(amps=avg_data,framerate=sample_rate)
    # wav.plot(scale_x=False)
    # plt.show()

    # spec = wav.to_spectrum()
    # spec.plot()
    # plt.show()

    # spec_total = spec_list[0]
    # for spectrum in spec_list[1:]:
    #     spec_total += spectrum
    # spec_total.hs  = spec_total.hs/(len(spec_list))
    # spec_total.plot()
    # plt.show()

    # incTable(filename)
    # s.saveData(data,row,None)

