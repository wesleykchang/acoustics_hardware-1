#!/usr/bin/python

from sys import argv
import sys
from serial import *
from time import sleep

if len(argv)<5:
	print "\nBad args!\n\nUsage: python serialcheck.py <PORT> <BAUD> <CHECK STRING> <CORRECT RESPONSE> [RN,R,N]\n\n(the last argument represents the optional line ending. default is RN=\\r\\n. it is necessary for now)\n"
	sys.exit()

args = argv[1:]

s = Serial(args[0],args[1],timeout=0.5)

lineEnding="\r\n"
if len(args)>=5:
	le=args[4]
	if le=="N":
		lineEnding="\n"
	elif le=="R":
		lineEnding="\r"
	elif le=="RN":
		lineEnding="\r\n"
	
#clear it
s.write(lineEnding)
sleep(0.5)
s.readlines()

s.write(args[2]+lineEnding)

sleep(0.5)
out = s.readlines()

out = [o.strip() for o in out]

if 0<len([0 for x in out if x==args[3]]):
	print "0"
else:
	print "1"

s.close()
