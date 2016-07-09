from pithy import *
import json 

#Get all JSON files in a given directory
alt = "/your_Data_dir/*.json" 
fils = glob(alt)

#if you have another data dir
#alt = "/otherdatadir//*/*.json" 
#fils2 = glob(alt)
#fils = fils+fils2

print len(fils)
#Find unique prefixes
dd = {}
for f in fils[:]:
    try: dd[f[:-16]] += 1
    except: dd[f[:-16]] = 0


#Define a threshold count to make a csv
threshold = 20

#Get Runs and Sort
keys = dd.keys()
keys.sort()
print len(keys)

#Where we'll dump the finished files
csv_dir = "/acoustic_csv_dir_or_whatever/"
go("mkdir "+csv_dir)
for k in keys:
    #If there are more than threshold runs make csv
    if dd[k] >= threshold:
        ff = glob(k+"*.json") #get all data in run
        ff.sort() #sort by filename (time)
        fn = csv_dir+k.split("/")[-1]+".csv"
        fn = fn.replace("'","") #make filename
        print fn
        #open(fn,'w').write("") #erase file if it exists
        #Find the number of lines in the file
        try:
            exist = len(open(fn).read().split("\n"))
        except:
            exist = 0
        print exist,len(ff)
        #for each file, open file, extract time of file and time between datapoints, and then make a line of all readings.  then append to csv.  depending on the comments above we'll just append the new data, or we'll overwrite the file entirely
        for f in ff[exist:]: 
            try:
                taq = f[-15:-5]
                data = json.load(open(f))
                dtus = str(mean(diff(data['time (us)'])))
                out = taq+", "+dtus+", "+str(data['amp'])[1:-1]+"\n"
                open(fn,"a").write(out)
                
            except Exception as E:
                print f,E




