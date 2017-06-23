#!/bin/bash

echo "deb http://labs.picotech.com/debian/ picoscope main" > /etc/apt/sources.list.d/picoscope.list
wget -O - http://labs.picotech.com/debian/dists/picoscope/Release.gpg.key | sudo apt-key add -
apt-get update

apt-get install picoscope
usermod -a -G pico lab
