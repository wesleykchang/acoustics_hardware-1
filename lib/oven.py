import time
import minimalmodbus as mb

class Oven():
    def __init__(self,port):
        self.port = port
        self.connect()

    def connect(self):
        self.conn = mb.Instrument(self.port,1)
        self.conn.serial.baudrate = 9600
        self.conn.serial.timeout = 0.1

    #TODO: how to handle checksum errors?
    def _read(self,register):
        try:
            return self.conn.read_register(register,1,signed=True)
        except ValueError as e: #happens sometimes when checksum fails...
            raise(e)  #do something about it...

    def _write(self,register,value):
        try:
            self.conn.write_register(register,value,1,signed=True)
        except ValueError as e: #happens sometimes when checksum fails...
            raise(e)  #do something about it...

    def get_temp(self):
        return self._read(100)

    def get_temp_setting(self):
        return self._read(300)

    def set_temp(self,temp,verify=True):
        self._write(300,temp)
        if not verify:
            return temp
        else:
            setting = self.get_temp_setting()
            if int(setting*10)==int(temp*10):
                return temp
            else:
                e = ValueError("Oven did not accept temp setting."+ \
                               "Should be {} but is {}.".format(temp,setting))
                raise(e)

    def log_temp(self,logfile,set_temp,temp,note=None):
        """Put unixtime,set_temp,actual_temp,notes in a logfile/csv"""
        msg = str(time.time())+","+str(set_temp)+","+str(temp)+","+str(note)+"\n"
        open(logfile,"a").write(msg)

    def go_to(self,temp,logfile=None):
        """Sets the temperature and blocks until the temperature is reached."""
        now = -1
        self.set_temp(temp)
        while int(now*10)/10!=temp:
            now = self.get_temp()
            if logfile is not None:
                self.log_temp(logfile,temp,now,"go")
            time.sleep(0.5)

    def hold_for(self,secs,setting,logfile=None):
        """Blocks and reads temperature until `secs` seconds have passed."""
        s = time.time()
        while time.time()-s<secs:
            now = self.get_temp()
            if logfile is not None:
                self.log_temp(logfile,setting,now,"hold")
            time.sleep(0.5)
