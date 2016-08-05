### EASI
___

# Dependencies:

- python 3 
- flask (`sudo pip3 install flask`)
- numpy (`sudo pip3 install numpy`)

# How to start daemons

-Start the nodeforwarder for the mux and epcoch.
- Navigate to the easi folder and open up acoustic_daemon.py. Pass the appropriate NF ports to the daemons.
- Scroll down to the main function. 
 - If you are just testing UI, uncomment the UI daemon from main. 
- The UI daemon will begin serving at localhost:5000 where you can view the interface. 
- If you are testing both UI and Acoustic daemons, uncomment the Acoustic Daemon in main. 
- Run python acoustic_daemon.py from the command line. You may need to chmod the file 'acoustic_daemon.py' . 
- Both daemons will begin running in the backgroud. You can view their PID files in the newly created Daemon_PIDs folder. To stop the daemons, simply call ' python stopdaemons.py' from the commandline in the easi folder (same folder you started the daemons).

#Notes on the Interface:

-Navigate to the address where you are hosting the table. From there you can add and delete rows. 
-Pressing the 'play' button will start a test and automatically generate both a timestamp and a testID. The testID is used to record all the details of the parameters passed a given test. Parameters cannot be edited after pressing play without pressing the stop button and creating a new test.
-Data is stored in the easi folder under a folder named 'Data'. Data is sorted by start date and testID. So the file path for 'Test 5' that began on August 3rd would be stored under 'Data/Aug_03_2016/TestID_5'
-From the interface, to view a log of all the tests that were started on a given day, navigate to 'host:port/startdate/view'. For example, "localhost:5000/Aug_03_2016/view" would show you all the tests that were started on August 3rd.
