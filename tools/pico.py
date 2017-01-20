import sys
sys.path.append('../EASI-analysis/analysis') 
import filesystem

import redpitaya

saver = filesystem.Saver()

rp = redpitaya.RedPitaya("169.254.1.10")
rp.prime_trigger()
wave = rp.get_waveform(delay=2,time=20)
row = {} #json of table_state!
saver.saveData(wave,row,None)
