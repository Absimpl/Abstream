import os, signal
import httplib, urllib,json
def Stop_Stream():
    processname = 'absimpl_abstream_housekeep.py'

    for line in os.popen("ps xa"):
        fields = line.split()        
        pid = fields[0]
        process = fields[4]
        if len(fields) > 5:           
            program = fields[5]
            if program.find(processname) >= 0:                 
        # Kill the Process. Change signal.SIGHUP to signal.SIGKILL if you like
                os.kill(int(pid), signal.SIGKILL)      
Stop_Stream()


