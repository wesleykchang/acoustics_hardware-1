import sys
import time
sys.path.append('../lib') 

import oven as oven

o = oven.Oven("/dev/ttyUSB2")

start_time = time.time()

#### Plan: get to 25C, drop to 0C, hold for 10 min, go up to 50C in 
#### increments of 5 degrees, return to 25C.

o.go_to(24,logfile="test_temp.csv")
o.hold_for(900,24,logfile="test_temp.csv")

for i in range(24,0,-3): #doesn't include 0C
    o.go_to(i,logfile="test_temp.csv")
    o.hold_for(900,i,logfile="test_temp.csv")

for i in range(0,51,3): #doesn't include 51C
    o.go_to(i,logfile="test_temp.csv")
    o.hold_for(900,i,logfile="test_temp.csv")

for i in range(51,23,-3):
    o.go_to(i,logfile="test_temp.csv")
    o.hold_for(900,i,logfile="test_temp.csv")

print("\n:)\n")


