
###TODO: Add signal handling 

import os
import sys
import time
import signal


class Daemon:
    def __init__(self,debugging=False,force=False):
        self.pid_file = "pid"
        self.pid = 0
        self.debugging = debugging
        self.cleanup(force=force)

    def cleanup(self,force=False):
        if self.pid_file_exists():
            pid = open(self.pid_file,"r").readlines()[0]
            if self.pid_exists(pid):
                if force:
                    self.debug("found old daemon at {}, killing.".format(pid))
                    os.kill(pid,signal.SIGKILL)
                else:
                    err = "Daemon is already running, PID: {}.".format(pid)\
                          + " Call with force=True if you want to kill it."
                    raise OSError(err)
            return
        else: #all good
            return

    def stop(self):
        if self.pid_file_exists():
            os.remove(self.pid_file)
            sys.exit(0)
        else: #wat?
            sys.exit(1)

    def start(self):
        if self.pid_file_exists():
            self.debug("Tried to start() but a pid is already recorded.")
            sys.exit()
        #first fork
        p = os.fork()
        if p>0:
            sys.exit(0)
        os.setsid() #also set umask?
        #second fork
        p = os.fork()
        if p>0:
            sys.exit(0)
        #okay, we're a daemon now
        pid = os.getpid()
        self.pid = pid
        self.write_pid(pid)
        try:
            self.run()
        finally:
            try:
                os.remove(self.pid_file)
            except FileNotFoundError:
                pass

    def write_pid(self,pid):
        if not self.pid_file_exists():
            open(self.pid_file,"w").write(str(pid))
        else:
            raise IOError("pid file is here when it's not supposed to be.")

    #this is mostly-verbatim from SO
    def pid_exists(pid):
        if os.name!="posix": #TODO: put this higher up in the tree
            raise OSError("Are you on Windows? this doesn't work on Windows")
        if pid < 0:
            return False
        if pid == 0: 
            raise ValueError('invalid PID 0')
        try:
            os.kill(pid, 0)
        except OSError as err:
            if err.errno == errno.ESRCH:
                # ESRCH == No such process
                return False
            elif err.errno == errno.EPERM:
                # EPERM clearly means there's a process to deny access to
                return True
            else: # possibles: (EINVAL, EPERM, ESRCH)
                raise
        else:
            return True

    def pid_file_exists(self):
        try:
            pid = open(self.pid_file,"r").read().strip()
            if len(pid)>0:
                return True
            else:
                return False
        except FileNotFoundError:
            return False

    #TODO: make this log somewhere, etc
    def debug(self,msg):
        if self.debugging:
            print(msg)
        return

    def run(self):
        raise NotImplementedError

class SupervisedDaemon(Daemon):
    def __init__(self,debugging=False,force=False):
        Daemon.__init__(debugging,force)
    def spawn(self):
        pass
    def kill(self,pid):
        pass
    def list(self):
        pass

#writes to a file for a while then kills itself. useful for testing
#daemon/supervisors
class Tester(Daemon):
    def run(self):
        print(self.pid)
        count = 0
        while True:
            open("tester","a").write(str(count)+"\n")
            count += 1
            if count>100:
                self.stop()
            time.sleep(1)

if False and __name__=="__main__":
    t = Tester()
    t.start()
