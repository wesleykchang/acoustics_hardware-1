from urllib.request import urlopen as uo
from time import sleep
import sys

class Mux():
    def __init__(self,url,fake=False):
        self.url = url
        self.on = []
        self.fake = fake #currently unused.

    def _get_switch_cmd(self,cmd):
	
        bits = cmd.split(" ")
        if bits[0] in ["U","L"]:
            module = int(bits[1])
            if module==0:
                return "L 2 0"
            elif module==1:
                return "L 2 1"
            elif module==3:
                return "L 2 2"
            elif module==4:
                return "L 2 3"
            elif module==5:
                return "L 7 0"
            elif module==6:
                return "L 7 1"
            elif module==8:
                return "L 7 2"
            elif module==9:
                return "L 7 3"
            else:
                raise(Exception("That's not a usable module!"))
        else:
            return ""

    def get(self):
        return self.on

    def _encodeChar(self,char):
        if char=="\r":
            return "%0D"
        elif char==" ":
            return "%20"
        elif char=="\n":
            return "%0A"
        else:
            return char

    def _prepCmdURLs(self,cmds):
        """Properly separates commands and splits lines, taking
        care to limit the maximum characters sent at once to 19.
        Returns list of urls to run (with a delay between them!)"""
        cmdset = ["",""] #force it to send a blank command first always
        for cmd in cmds:
            if len(cmdset[-1]+cmd)+1 >= 19: #max length mux can read is 19
                cmdset.append(cmd+";")
            else:
                cmdset[-1] += cmd + ";"
        new = []
        for cs in cmdset:
            cs+="\r\n"
            new.append("".join([self._encodeChar(c) for c in cs]))
        return new

    def sendCommands(self,cmds,delay):
        for c in cmds[:]:
            new = self._get_switch_cmd(c)
            if new != "":
                cmds.append(new)
        urls = self._prepCmdURLs(cmds)
        reads = []
        for u in urls:
            uo(self.url+"/write/"+u).read()
            sleep(delay) #hope this is long enough! try 0.2
            red = uo(self.url+"/read/").read()
            if u!="%0D%0A": #don't bother reporting blank cmds
                reads.append(red)
        return reads
            
    def latch(self,channel_list,clear_first=True,delay=0.2):
        """channel_list should be (module,channel) pairs."""
        if clear_first:
            cmdset = ["C"]
        else:
            cmdset = []
        for ch in channel_list:
            module = ch[0]
            channel = ch[1]
            cmd = "L {} {}".format(int(module),int(channel))
            cmdset.append(cmd)
        return self.sendCommands(cmdset,delay=delay)
        
    def unlatch(self,channel_list,delay=0.2):
        #this should fail and give an error of 6 or 7, but
        #instead it just falls through. without it, the first real 
        #command isn't registered... TODO: Figure out why.
        cmdset = []
        for ch in channel_list:
            module = ch[0]
            channel = ch[1]
            cmd = "U {} {}".format(int(module),int(channel))
            cmdset.append(cmd)
        return self.sendCommands(cmdset,delay=delay)

    def clearAll(self,delay=0.2):
        return self.sendCommands(["C"],delay=delay)

    def switch(self,chan,chan2=None,delay=0.2):
        try:
            # realchan = self.channel_map[int(chan)]
            #0,3
            a,b = chan.split(",")
            realchan = [(int(a),int(b))]
            if chan2 is None:
                realchan2 = []
            else:
                c,d = chan2.split(",")
                realchan2 = [(int(c),int(d))]
            self.latch(realchan+realchan2,delay=delay,clear_first=True)
            self.on = [chan,chan2]
            return self.on
        except Exception as E: #TODO: custom errors and handlers. FIX THIS don't be lazy
            print("problem with mux")
            raise(E)

if __name__=="__main__":
    m = Mux("http://localhost:9002")
    print(m.clearAll()) 
    print(m.switch(43,64))
