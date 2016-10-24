# settings = {"tr" : "M1", "pe" : "M0"}
# defaults = {"ok" : "dokey"}

# try:
# 	settings["ok"]
# except KeyError as e:
# 	settings[e.args[0]] = defaults[e.args[0]]

# print (settings["ok"])
import xlrd
import pickle
import collections
from pprint import pprint

d = {}
wb = xlrd.open_workbook('../../CP-pulsetable.xlsx')
sh = wb.sheet_by_index(0)

newindex = 2286

for i in range(1,65):
    cell_value_class = sh.cell(i,1).value
    cell_value_id = sh.cell(i,0).value
    if int(cell_value_class) in list(d.keys()):
    	d[newindex] = int(cell_value_id)
    	newindex += 1
    else:
    	d[int(cell_value_class)] = int(cell_value_id)

for i in range(1,65):
    cell_value_class = sh.cell(i,3).value
    cell_value_id = sh.cell(i,2).value
    if int(cell_value_class) in list(d.keys()):
    	d[newindex] = int(cell_value_id)
    	newindex += 1
    else:
    	d[int(cell_value_class)] = int(cell_value_id)

for i in range(1,65):
    cell_value_class = sh.cell(i,5).value
    cell_value_id = sh.cell(i,4).value
    if int(cell_value_class) in list(d.keys()):
    	d[newindex] = int(cell_value_id)
    	newindex += 1
    else:
    	d[int(cell_value_class)] = int(cell_value_id)

for i in range(1,62):
    cell_value_class = sh.cell(i,7).value
    cell_value_id = sh.cell(i,6).value
    if int(cell_value_class) in list(d.keys()):
    	d[newindex] = int(cell_value_id)
    	newindex += 1
    else:
    	d[int(cell_value_class)] = int(cell_value_id)




sKeys = sorted(list(d.keys()))
# print (d.keys())

d2 = collections.OrderedDict()
for key in sKeys:
	d2[key] = d[key]

# print (d2[1450])
pickle.dump(d2, open('CP_LUT','wb'))
# d2 = pickle.load(open('CP_LUT','rb'))
# print(d2[2150])
# pprint(d2)
# json.dump(d, open('CP_LUT','w'))