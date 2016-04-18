#!/usr/bin/python

###### INCOMPLETE DON'T USE THIS YET

from sys import argv
import sys
from commands import getoutput as go

def checkPort(port,baud,ping,pong,line_end="\r\n",timeout=0.1):
    s = Serial(port,baud,timeout=timeout)
	
    #flush it
    s.write(line_end)
    sleep(0.1)
    s.readlines()

    #see what's there
    s.write(ping+line_end)
    sleep(0.1)
    out = s.readlines()
    out = [o.strip() for o in out]

    if 0<len([0 for x in out if x==pong]):
            return True
    else:
            return False

##### print info and confirm args
if len(argv)==1:
    print "\nNo arguments given. Going to search for things over USB and connect them to default ports.\n"
    siui=False
else:
    args = argv[1:]
    try:
        ip = [int(x) for x in args[0].split(".") if int(x)<255 and int(x)>0]
        if len(ip)!=4:
            1/0
    except:
        print "\n'"+args[0]+"' is not a valid IP address. Exiting.\n"
        sys.exit()
    siuiIP = ip
    siui = True

##### check ifconfig, fix if needed
if siui:
    ifconfig = go("/sbin/ifconfig eth0").split(" ")
    i = ifconfig.index("inet")
    print ifconfig[i+1]

    ##### find SIUI

##### find mux

##### start errthing
