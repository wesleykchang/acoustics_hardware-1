from glob import glob
import os 
from datetime import date
foo = glob("/Users/j125mini/EASI/pithy/code/*.py")
foo = sorted(foo, key=os.path.getmtime)
foo.reverse()



for i in foo:
    p = i
    i = i.split("/")[-1].replace(".py","")
    if i != "temper":
        print "<a href='"+i+"'>"+i+"</a> %s " % date.fromtimestamp(os.path.getmtime(p))