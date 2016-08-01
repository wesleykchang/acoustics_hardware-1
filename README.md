### EASI
___

#Dependencies:

- python 3 
- flask (`sudo pip3 install flask`)
- numpy (`sudo pip3 install numpy`)

# How to start daemons

- Navigate to the easi folder and open up acoustic_daemon.py. 
- Scroll down to the main function. 
 - If you are just testing UI, uncomment the UI daemon from main. 
- The UI daemon will begin serving at localhost:5000 where you can view the interface. 
- If you are testing both UI and Acoustic daemons, uncomment the Acoustic Daemon in main. 
- Make sure you have Node forwarder running with the Epoch, right now the Acoustic daemon defaults the epoch port to locahost:9003 but that can be changed. 
- Run python acoustic_daemon.py from the command line. You may need to chmod the file 'acoustic_daemon.py' . 
- Both daemons will begin running in the backgroud. You can view their PID files in the newly created Daemon_PIDs folder. To stop the daemons, simply call ' python stopdaemons.py' from the commandline in the easi folder (same folder you started the daemons).