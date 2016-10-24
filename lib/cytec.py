from urllib.request import urlopen as uo
from time import sleep
import sys

class Mux():
    def __init__(self,url,fake=False):
        self.url = url
        self.on = []
        self.fake = fake #currently unused.
        self.channel_map = \
                { 1:[(0,0)],  2:[(0,1)],  3:[(0,2)],  4:[(0,3)], 
                  5:[(0,4)],  6:[(0,5)],  7:[(0,6)],  8:[(0,7)],
                  9:[(1,0)], 10:[(1,1)], 11:[(1,2)], 12:[(1,3)],
                 13:[(1,4)], 14:[(1,5)], 15:[(1,6)], 16:[(1,7)],
                 17:[(2,0)], 18:[(2,1)], 19:[(2,2)], 20:[(2,3)],
                 21:[(2,4)], 22:[(2,5)], 23:[(2,6)], 24:[(2,7)],
                 25:[(3,0)], 26:[(3,1)], 27:[(3,2)], 28:[(3,3)],
                 29:[(3,4)], 30:[(3,5)], 31:[(3,6)], 32:[(3,7)],
                 33:[(4,0)], 34:[(4,1)], 35:[(4,2)], 36:[(4,3)],
                 37:[(4,4)], 38:[(4,5)], 39:[(4,6)], 40:[(4,7)],
                 41:[(5,0)], 42:[(5,1)], 43:[(5,2)], 44:[(5,3)],
                 45:[(5,3)], 46:[(5,5)], 47:[(5,6)], 48:[(5,7)],
                 49:[(6,0)], 50:[(6,1)], 51:[(6,2)], 52:[(6,3)],
                 53:[(6,4)], 54:[(6,5)], 55:[(6,6)], 56:[(6,7)],
                 57:[(7,0)], 58:[(7,1)], 59:[(7,2)], 60:[(7,3)],
                 61:[(7,4)], 62:[(7,5)], 63:[(7,6)], 64:[(7,7)]}

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
                cmdset.append(cmd)
            else:
                cmdset[-1] += cmd + ";"
        new = []
        for cs in cmdset:
            cs+="\r\n"
            new.append("".join([self._encodeChar(c) for c in cs]))
        return new

    def sendCommands(self,cmds,delay):
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
            realchan = self.channel_map[int(chan)]
            if chan2 is None:
                realchan2 = []
            else:
                realchan2 = self.channel_map[int(chan2)]
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
