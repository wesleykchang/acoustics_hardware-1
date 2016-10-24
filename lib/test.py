import os
import json

# try:
# 	text_file = open("Data/Random/Output.txt", "w")
# except FileNotFoundError:
# 	# os.mkdir("Data")
# 	os.makedirs("Data/Random")
# 	text_file = open("Data/Random/Output.txt", "w")

# text_file.write("Blah.")
# text_file.close()

# d = {'anne' : 'wilkinson', 'belle' : 'dog'}

# try:
# 	info = json.load(open('test.json'))
# 	info['data'].append(d) #append to the list of dicts
# 	json.dump(info, open('test.json', 'w'))

# except FileNotFoundError:
# 	info = {'data' : []}
# 	info['data'].append(d) #append to the list of dicts
# 	json.dump(info, open('test.json', 'w'))


# def parse_URL(URL, host=None):
# 	if str(URL).isdigit():
# 		out = "http://localhost:" + str(URL)
# 	else:
# 		out = URL
# 	return out

import sys


if __name__ == "__main__":
	sys.stdout = open('file', 'a')
	print ('test')