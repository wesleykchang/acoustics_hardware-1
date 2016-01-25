#!/bin/bash

set -m #for fg/bg and forking

os=$(uname)

#find open serial ports
if [ $os == "Linux" ]; then
	ports=$(ls /dev | sed -n 's:\(.*tty[UA][SC][BM].*\):/dev/\1:p')
elif [ $os == "Darwin" ]; then
	ports=$(ls /dev | sed -n 's:\(.*tty\.usb.*\):/dev/\1:p')
else 
	echo "I don\'t know what os this is!"
fi

#check each port for Ephoch,SIUI,mux
#... not using assoc arrays because old bash

equip=() # use 0:epoch, 1:mux, 2:siui

probe () {
	p=$1
	baud=$2
	ping=$3
	pong=$4
	pcmd="equip[$p]"
	end=$5
	cmd="python serialcheck.py $p $baud $ping $pong $end"
	out=eval $cmd
	echo $out
}

echo ""
printf "Reading/verifying previous port locations...\n"
if [ -r porthistory.dat ]; then
	source porthistory.dat
    for p in $equip[*]; do
        if [ ! -e p ]; then
            :
        else
           printf "ports changed, ignoring..."
           equip=()
           break
       fi
    done
	echo "" > porthistory.dat
	if [ ${equip[0]} ]; then #is there a port already? make sure it's right
		out=$(probe ${equip[0]} 115200 "BATTSTAT?" "OK")
		if [ $out -eq 0 ]; then
			echo ">> EPOCH (still) on ${equip[0]} <<"
			echo "equip[0]=${equip[0]}" >> porthistory.dat
		else
			unset equip[0]
		fi
	fi
	if [ ${equip[1]} ]; then
		unset out
		out=$(probe ${equip[1]} 57600 "02" "2")
		if [ $out -eq 0 ]; then
			echo ">> MUX (still) on ${equip[1]} <<"
			echo "equip[1]=${equip[1]}" >> porthistory.dat
		else
			unset equip[1]
		fi
	fi
	if [ ${equip[2]} ]; then
		:
	fi
	printf "done.\n"
else
	printf "not found. We'll find them manually.\n"
	touch porthistory.dat
fi

printf "Probing USB ports for other equipment... "
for p in $ports; do
	if [ ! ${equip[0]} ]; then #have we set it yet?
		out=$(python serialcheck.py $p 115200 "BATTSTAT?" "OK");
		if [ $out == 0 ]; then
			printf "\n>> EPOCH on $p <<\n"
			equip[0]=$p #found it; store port for later
			echo "equip[0]=$p" >> porthistory.dat
		fi
	fi
	if [ ! ${equip[1]} ]; then
		out=$(python serialcheck.py $p 57600 "02" "2");
		if [ $out == 0 ]; then
			printf "\n>> MUX on $p <<\n"
			equip[1]=$p
			echo "equip[1]=$p" >> porthistory.dat
		fi
	fi
	if [ ! ${equip[2]} ]; then
		: #siui code goes here
	fi
done
echo "done."

if [ ${equip[0]} ]; then
	printf "Connecting EPOCH to port 9004... "
	echo "" > logs/epoch.log
	nodejs epoch/EpochForwarder.js 9004 ${equip[0]} 115200 10000  >> logs/epoch.log 2>&1 & epochpid=$! 
	sleep 6
	if [ -n $(ps -p $epochpid > /dev/null) ]; then
		printf "done.\n"
	else
		printf "ERROR\n"
		printf "Check log in ./logs/epoch.log\n"
		exit 1
	fi
fi
if [ ${equip[1]} ]; then
	printf "Connecting MUX to port 9003... "
	echo "" > logs/mux.log
	nodejs epoch/EpochForwarder.js 9003 ${equip[1]} 57600 10000  >> logs/mux.log 2>&1 & muxpid=$! 
	sleep 6 
	if [ -n $(ps -p $muxpid > /dev/null) ]; then
		printf "done.\n"
	else
		printf "ERROR\n"
		printf "Check log in ./logs/mux.log\n"
		exit 1
	fi
fi

printf "Starting pithy server on port 9001... "
echo "" > logs/pithy.log
cd pithy && node index.js 9001 >> logs/pithy.log 2>&1 & pithypid=$!
sleep 6 
if [ -n $(ps -p $pithypid > /dev/null) ]; then
    printf "done.\n"
else
    printf "ERROR\n"
    printf "Check log in ./logs/pithy.log\n"
    exit 1
fi

printf "Starting ethercalc on port 9002... "
echo "" > logs/pithy.log
    cd ethercalc/node_modules/ethercalc/bin && node ethercalc --port 9002 >> logs/ether.log 2>&1 & etherpid=$!
sleep 6 
if [ -n $(ps -p $etherpid > /dev/null) ]; then
    printf "done.\n"
else
    printf "ERROR\n"
    printf "Check log in ./logs/ethercalc.log\n"
    exit 1
fi


echo ""
echo "All good, here's some info:"
echo "EPOCH     PID: $epochpid      Port: 9004"
echo "MUX       PID: $muxpid        Port: 9003"
echo "pithy     PID: $pithypid      Port: 9001"
echo "ethercalc PID: $pithypid      Port: 9002"
echo "Output from this session will be in the logs/<device>.log files"
echo "Have fun! :)"
echo ""
#echo ${equip[*]}
