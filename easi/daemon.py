
###TODO: Add signal handling 

import os
import sys
import time
import signal
import errno

class Daemon:
    def __init__(self, run_fn=None, name=None, handler=None, force=False):
        self.pid_file = "pid_{}".format(name)
        self.pid = 0
        self.cleanup(force=force)
        self.run_fn = run_fn
        self.name = name
        if handler is None:
            self.handler = self.default_handler
        else:
            self.handler = handler

    def cleanup(self, force=False):
        if self.pid_file_exists():
            pid = int(open(self.pid_file, "r").readlines()[0])
            if self.pid_exists(pid):
                if force:
                    self.debug("found old daemon at {}, killing.".format(pid))
                    os.kill(pid, signal.SIGKILL)
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
        if p > 0:
            sys.exit(0)
        os.setsid() #also set umask?
        #second fork
        p = os.fork()
        if p > 0:
            return p #return the pid before exiting second parent
        #okay, we're a daemon now
        pid = os.getpid()
        self.pid = pid
        self.write_pid(pid)
        try:
            self.handler(run_fn)
        finally:
            try:
                os.remove(self.pid_file)
            except FileNotFoundError:
                pass

    #hurr durr why am I bothering?
    def default_handler(self,run_fn):
        try:
            run_fn()
        except Exception as e:
            raise e
        finally:
            pass

    def write_pid(self,pid):
        if not self.pid_file_exists():
            open(self.pid_file,"w").write(str(pid))
        else:
            raise IOError("pid file is here when it's not supposed to be.")

    def pid_exists(self,pid):
        if os.name != "posix": #TODO: put this higher up in the tree
            raise OSError("Are you on Windows? this doesn't work on Windows")
        return os.path.exists("/proc/{}".format(pid))

    def pid_file_exists(self):
        try:
            pid = open(self.pid_file,"r").read().strip()
            return len(pid) > 0
        except FileNotFoundError:
            return False

    #TODO: make this log somewhere, etc
    def debug(self, msg):
        if __debug__:
            print(msg)
        return

#writes to a file for a while then kills itself. useful for testing daemon
class Tester(Daemon):
    def __init__(self):
        Daemon.__init__(self, run_fn=self.run_fn, name="poop")
    def run_fn(self):
        print(self.pid)
        count = 0
        while True:
            open("tester", "a").write(str(count)+"\n")
            count += 1
            if count > 10:
                self.stop()
            time.sleep(1)

if __name__ == "__main__":
    t = Tester()
    pid = t.start()

