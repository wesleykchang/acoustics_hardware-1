#!/usr/bin/env python3
'''
prompts the user to plug in various hardware components
and pairs them to udev rules
'''

import os
import subprocess
import time
import shutil

path = '/etc/udev/rules.d/'
usb_fname = '96-serial-usb.rules'


def get_dev():
    return os.listdir('/dev')


def get_udevadm_info(devpath):
    udev_info = (subprocess.check_output(['udevadm', 'info', devpath])).decode('utf-8')
    udev_info = udev_info.split('\n')

    abs_path = [x for x in udev_info if 'DEVPATH=/devices' in x][0]
    abs_path = abs_path.split('=')[-1]
    
    #get just ENV variables
    env_info = [x[3:] for x in udev_info if x[:2] == 'E:']

    
    #filter out all the usb port specific stuff
    unique_info = [x for x in env_info
                   if 'USB' not in x.split('=')[1].upper()
                   and 'USEC_INITIALIZED' not in x.split('=')[0]
                   and 'MINOR=' not in x
                   and 'MAJOR=' not in x
                   and ':' not in x
                   ]
    return unique_info, abs_path


def udev_add_string(arr, symlink):
    s = 'ACTION=="add"'
    s += ', RUN+="/bin/bash '+path+'scripts/'+symlink+'.sh"'
    s += ', SYMLINK+="'+symlink+'"'
    for item in arr:
        item = ', ENV{'+item
        item = item.replace('=', '}=="')
        item += '"'
        s += item
    return s


def udev_rm_string(arr, symlink):
    s = 'ACTION=="remove"'
    s += ', RUN+="/bin/bash '+path+'scripts/'+symlink+'_rm.sh"'
    for item in arr:
        item = ', ENV{'+item
        item = item.replace('=', '}=="')
        item += '"'
        s += item
    return s


# wipe old udev file
with open(path+usb_fname, 'w') as f:
    pass

all_names = [
    'nfcp',
    'nfmux',
    'pico'
    ]

serial_names = [
    'nfcp',
    'nfmux'
    ]

######CREAETE SCRIPTS#######
# script_path = path+'scripts/'
# if os.path.exists(script_path):
#     shutil.rmtree(script_path)
# os.makedirs(script_path)

# for name in all_names:
#     with open(script_path+name+'.sh', 'w') as f:
#         f.write('/usr/bin/docker start '+name)
#     with open(script_path+name+'_rm.sh', 'w') as f:
#         f.write('/usr/bin/docker stop '+name)

        
#######PICOSCOPE#############################
if not os.path.exists(path+'95-pico.rules'):
    raise ValueError('Picoscope not installed yet! Do that first')

# with open(path+'95-pico.rules', 'r') as f:
#     s = f.read().split('\n')[0]

add_s = 'ATTRS{idVendor}=="0ce9", MODE="664", GROUP="pico", ACTION=="add", RUN+="/bin/bash '+path+'scripts/pico.sh", SYMLINK+="pico"'
rm_s = 'ENV{ID_VENDOR_ID}=="0ce9", ACTION=="remove", RUN+="/bin/bash '+path+'scripts/pico_rm.sh"'

with open(path+'95-pico.rules', 'w') as f:
    # f.write(s+'\n')
    f.write(add_s+'\n')
    f.write(rm_s+'\n')

x = subprocess.check_output(['/etc/init.d/udev', 'restart'])
print('Plug in the Picoscope Now:')
while 'pico' not in get_dev():
    time.sleep(0.1)


########SERIAL ADAPTER EQUIPMENT######################
abs_paths = []

for name in serial_names:

    # Wait for plugin
    devs = set(get_dev())
    print('Plug in the '+name+' Now:')
    diff = devs.symmetric_difference(set(get_dev()))
    while not diff:
        diff = devs.symmetric_difference(set(get_dev()))

    print('Processing...')
    devpath = '/dev/'+list(diff)[0]
    time.sleep(3) # need this to fully establish connection

    #get udev info
    udevadm, abs_path = get_udevadm_info(devpath)
    abs_paths.append(abs_path)

    #stringify udev info
    add_s = udev_add_string(udevadm, name)
    rm_s = udev_rm_string(udevadm, name)

    #write udev rule
    with open(path+usb_fname, 'a') as f:
        f.write(add_s+'\n')
        f.write(rm_s+'\n')

    print('\nDone! Please dont unplug it\n')
    

#######RESET UDEV#############################
print('Restarting udev process...')
x = subprocess.check_output(['/etc/init.d/udev', 'restart'])
for abs_path in abs_paths:
    x = subprocess.check_output(['udevadm', 'test', '--action=add', abs_path], stderr=subprocess.STDOUT)


print('Starting up scripts')
for name in serial_names:
    if name in get_dev():
        x = subprocess.check_output(['/bin/bash', script_path+name+'.sh'])

print('Finished!')
