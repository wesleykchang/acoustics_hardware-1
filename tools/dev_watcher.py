import os
import subprocess
import sys
import threading
import queue

class DW():

    def __init__(self):

        if len(sys.argv) == 1:
            self.names = [
                'nfcp',
                'nfmux',
                'pico',
            ]
        else:
            self.names = sys.argv[1:]

        self.queue = queue.Queue()

        self.cmd_thread = threading.Thread(target=self.daemon_loop, daemon=True)
        self.cmd_thread.start()
        devs = self.get_dev()
        for name in self.names:
            if name in devs:
                self.add_command(name, mode='start')
            else:
                self.add_command(name, mode='stop')

    def daemon_loop(self):
        while True:
            cmd = self. queue.get()
            if cmd:
                self.run_command(cmd)

    def add_command(self, name, mode='start'):
        self.queue.put([mode, name])

    def run_command(self, cmd):
        if cmd:
            print(cmd[0], cmd[1])
            try:
                subprocess.check_output(['/usr/bin/docker', *cmd])
            except subprocess.CalledProcessError as e:
                print(e.output)

    def get_dev(self):
        return os.listdir('/dev')

    def dev_loop(self):
        devs = set(self.get_dev())
        diff = set(self.get_dev())
        add = diff - devs
        subtract = devs - diff
        while not add and not subtract:
            diff = set(self.get_dev())
            add = diff - devs
            subtract = devs - diff

        for dev in list(add):
            if dev in self.names:
                self.add_command(dev, mode='start')

        for dev in list(subtract):
            if dev in self.names:
                self.add_command(dev, mode='stop')

    def loop(self):
        while True:
            self.dev_loop()

if __name__ == '__main__':
    dw = DW()
    dw.loop()
