from urllib.request import urlopen as uo
from time import sleep
import sys

class Mux():
    def __init__(self,url):
        self.url = url

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

    def sendCommands(self,cmds):
        urls = self._prepCmdURLs(cmds)
        reads = []
        for u in urls:
            uo(self.url+"write/"+u).read()
            sleep(0.2) #hope this is long enough!
            red = uo(self.url+"read/").read()
            if u!="%0D%0A": #don't bother reporting blank cmds
                reads.append(red)
        return reads
            
    def latch(self,channel_list,clear_first=True):
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
        return self.sendCommands(cmdset)
        
    def unlatch(self,channel_list):
        #this should fail and give an error of 6 or 7, but
        #instead it just falls through. without it, the first real 
        #command isn't registered... TODO: Figure out why.
        cmdset = []

        for ch in channel_list:
            module = ch[0]
            channel = ch[1]
            cmd = "U {} {}".format(int(module),int(channel))
            cmdset.append(cmd)
        return self.sendCommands(cmdset)

    def clearAll(self):
        return self.sendCommands(["C"])

if __name__=="__main__":
    m = Mux("http://localhost:9000/")
    print(m.latch([(0,0)]))
    print(m.unlatch([(0,0)]))
