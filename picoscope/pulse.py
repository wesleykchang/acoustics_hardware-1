from picoscope.picoscope import Picoscope2000

def pulse(picoscope_: Picoscope2000, params: dict):
    pass


    ## FROM LEGACY

    # def get_waveform(self,
    #                     pct_diff_avg_cutoff=0.1,
    #                     wait_for_trigger=True,
    #                     return_waves=False):
    #     """
    #     The maximum sampling rate of the scope is 500MHz (2ns resolution).
    #     By default, it is set to that.
    #     Discards waves whose amp-sum is pct_diff_avg_cutoff away from mean
    #     """
    #     if wait_for_trigger:
    #         self.ps.waitReady()
    #     waves = self.read()

    #     #amp_sum = list(map(np.sum, map(abs, waves)))
    #     #m = np.mean(amp_sum)
    #     #amp_sum_pct = np.abs(np.divide(np.subtract(amp_sum, m), m))
    #     #waves_avg = np.array(waves)[amp_sum_pct < pct_diff_avg_cutoff]

    #     data = np.mean(np.transpose(waves), axis=1).tolist()
    #     t = np.arange(self.nsamples) * (1 / self.sample_rate) * 1e6
    #     t = t.tolist()
    #     if return_waves:
    #         return waves
    #     else:
    #         return [t, data]


# #function that actually grabs a wave from the pico
# #PULSER MUST BE RUNNING AT A DECENT RATE (>50 pulses/sec) FOR THIS
# @app.route('/get_wave', methods=['POST'])
# def getter():
#     global t
#     x = flask.request.values
#     delay = float(x['delay'])
#     duration = float(x['duration'])

#     if 'avg_num' in x:
#         ps.set_averaging(int(x['avg_num']))
#     else:
#         ps.set_averaging(32)

#     if 'sample_rate' in x:
#         ps.set_sample_rate(float(x['avg_num']))
#     else:
#         ps.set_sample_rate(5e8)

#     if 'voltage' in x:
#         maxV = x['voltage']
#         if 'auto' in maxV:
#             ps.auto_range(delay, duration)
#         else:
#             maxV = float(maxV)
#             ps.set_maxV(maxV)
#     else:
#         ps.auto_range(delay, duration)

#     ps.prime_trigger(delay, duration)
#     t_series, data = ps.get_waveform()

#     ret_data = {'data': data, 'framerate': ps.sample_rate}
#     t = int(time.time() * 1000)
#     return json.dumps(ret_data)
