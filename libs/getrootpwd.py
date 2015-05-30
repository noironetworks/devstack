#!/usr/bin/env python
import sys
from passwdlib import *

if __name__ == "__main__":
    ret = getpasswd(sys.argv[1])
    if ret == "printmessage":
        print "git.insieme.local is not reachable, neither is 10.160.1.12:11011"
        print "Looks like DMZ zone. Create a ssh tunnel between git.insieme.local and this host"
        print "Example:i On a system in cisco network run the following commands"
        print "    ssh -R 0.0.0.0:11011:172.23.137.25:80  -p 112 -N -f dmz@173.36.240.158"
        print "(GatewayPorts should be set to yes in sshd config of dmz jumpserver)"
        sys.exit(1)
    else:
        print ret

