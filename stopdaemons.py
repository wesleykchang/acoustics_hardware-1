import os
import sys
import signal
import time

"""Script that goes through and stops any running daemons based off of pid files.
There's probably a better way to do this but this should work for now.

TO DO: potentially add argparser so you can specify daemon to stop or to stop all from terminal."""

def stop_daemon(pid_file):
        pid = int(open(pid_file, "r").readlines()[0])
        try:
                os.kill(pid, signal.SIGTERM) #to hopefully shut down SCPI cleanly
                time.sleep(0.1)
        except OSError: #process doesn't exist in the first place
                pass
        try:
                os.kill(pid, signal.SIGKILL)
        except OSError: #SIGTERM worked
                pass
        os.remove(pid_file)
        return

def stop_all_daemons():
        for pid_file in os.listdir('Daemon_PIDs'):
                stop_daemon(os.path.join('Daemon_PIDs',pid_file))
        try:
                os.rmdir('Daemon_PIDs')
        except(OSError):
                pass
        return

if __name__ == "__main__":
        if len(sys.argv) > 1:
                for daemon in sys.argv[1:]:
                        pid_file = ''.join(('pid_',daemon))
                        stop_daemon(os.path.join('Daemon_PIDs',pid_file))
        else:
                stop_all_daemons()
