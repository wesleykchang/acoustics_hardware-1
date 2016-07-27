import os
import sys
import signal

"""Script that goes through and stops any running daemons based off of pid files.
There's probably a better way to do this but this should work for now.

TO DO: potentially add argparser so you can specify daemon to stop or to stop all from terminal."""

def stop_daemon(pid_file):
	pid = int(open(pid_file, "r").readlines()[0])
	os.kill(pid, signal.SIGKILL)
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
	stop_all_daemons()