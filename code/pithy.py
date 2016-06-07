import numpy
import numbers
import scipy
from scipy import ndimage
from scipy import integrate
from scipy import special
from scipy import signal
import matplotlib
matplotlib.use('agg')
from pylab import *
from PIL import Image
from PIL import ImageOps
from glob import glob
try:
    from markdown import markdown as md
except:
    iam ="graceful"
import time
import os
import sys
from commands import getoutput as go
import inspect
import StringIO
import urllib, base64
#import matplotlib.pyplot as plt,mpld3
#import mpld3
#from quiner import whos
#import atexit
import __main__

def exit_handler(m,ls):
    print "should be doing stuff"
    whos(ls,fil=m)



fig, ax = plt.subplots()

sys.path.append('/home/dan/sandbox/peak-o-mat-1.1.9/')

#Figure Defaults
rcParams['font.family'] = "Arial"


#hack to make things worth from PIL

def showint():
    print mpld3.fig_to_d3(fig).replace("\n","\r")

def himg(fn):
    print "<img src='%s'>" % fn 

def showimg(im,tip=".png",width=None,dpi=150):
    tim = str(int(time.time()))    
    #imname = imname.replace("/","-")
    image = 'images/pithy_img_'+str(int(time.time()*1000))+tip
    im.save(image,dpi=dpi)
    
    if width != None:
        print "<img src='%s' style='width:%s'>" % (image,str(width)),
    else: print '##_holder_##:',"/"+image
    

def showme(tip="png",kind="static",width=None,height=None,inline=False,dpi=80):
    tim = str(int(time.time()))	
    #imname = imname.replace("/","-")
    image = 'images/pithy_img_'+str(int(time.time()*1000))+"."+tip
    w = ""
    h = ""
    if width != None: w = "width:"+str(width)+"px;"
    if height != None: h = "height:"+str(height)+"px;"
    s = "style='%s%s'" %(w,h)
    #strang = '<img '+s+' src=/'+image+'>'
    if kind == "static": 
        print imager64(tip=tip,dpi=dpi,style=s),
        if not inline: print ""

    else: 
        savefig(image,dpi=dpi,bbox_inches="tight")
        print '##_dynamic_##:',kind,':',tim,':',"/"+image




def imager64(tip="png",dpi=80,style=None):
    imgdata = StringIO.StringIO()
    savefig(imgdata,dpi=dpi,tip=tip,bbox_inches="tight")
    imgdata.seek(0)  # rewind the data
    preload = 'data:image/%s;base64,'% tip 
    if tip == "svg":
        preload = 'data:image/svg+xml;;base64,' 
    uri =  preload+urllib.quote(base64.b64encode(imgdata.buf))
    return '<img %s src = "%s"/>' % (style,uri)

#A smoothing function I use
def smooth(x,window_len=11,window='flat'):
    if x.ndim != 1:
        raise ValueError, "smooth only accepts 1 dimension arrays."

    if x.size < window_len:
        raise ValueError, "Input vector needs to be bigger than window size."


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError, "Window is on of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"


    s=numpy.r_[x[window_len-1:0:-1],x,x[-1:-window_len:-1]]
    #print(len(s))
    if window == 'flat': #moving average
        w=numpy.ones(window_len,'d')
    else:
        w=eval('numpy.'+window+'(window_len)')

    y=numpy.convolve(w/w.sum(),s,mode='valid')
    
    y = list(y)
    #account for windowing shift 2012-08-02
    for j in range(0,int(window_len)):
        y.pop(0)

    
    return array(y)



#makes links to quick go between 
def navigator():
    me  = ""
    mess = sys.argv
    mess[0] = mess[0].split("/")[-1].replace(".py","")
    for m in mess:
        me += m+"/"
    base = "http://steingart.princeton.edu"
    code = ":8001/"
    view = ":8003/"
    cl = base+code+me
    vl = base+view+me
    print "<a href='%s'>view</a> | <a href='%s'>code</a>" % (vl,cl)


def strrip(string,ff,fl):
    part1 = string.find(ff)
    part2 = string.find(fl)
    return string[part1+len(ff):part2]

#line # hack from http://code.activestate.com/recipes/145297-grabbing-the-current-line-number-easily/
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

def refresh(interval = 5):
    print "<meta http-equiv='refresh' content='%i'>" % interval


#site specific
drop_pre = "/var/drops/files/"
drop_pre_link = "http://steingart.princeton.edu:8002/static/realfiles/"



clf()

if __name__ == "__main__":
    print rcParams['figure.figsize']
    print rcParams['figure.dpi']

    navigator()