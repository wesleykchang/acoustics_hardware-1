from pithy import *
import psutil
import sys

#this is just used as a hack to kill python processes that won't die.
listing = psutil.get_pid_list()
for p in listing:
    process = psutil.Process(p)
    # print process
    if process.name() == 'python' or process.name() == 'Python':
        # print 'here'
        try: 
            print process.cmdline()
            pass
        except:
            print 'index error'
            pass
        try:
#insert file name in line below
            if "example-acoustic" in process.cmdline()[2]: #this is the important line where you 'select' what process you want to kill.
                print 'process ', process
                # print process.cmdline()[2]
                #print process.cmdline[2]
                process.terminate()
                print "terminated \n\n\n\n\n\n"
                print process
        except:
            print 'other error'
        