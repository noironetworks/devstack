#!/usr/bin/env python

import urllib2
import time
import re
import os
import sys
import pexpect
import xml.etree.ElementTree as ET

def isurlreachable(url):
    request = urllib2.Request(url)
    try:
        response = urllib2.urlopen(request)
    except:
        return False
    else:
        return True

def generateToken(challenge, url):
    numTries = 100
    delay = 1
    while numTries > 0:
        numTries = numTries - 1
        try:
            #print "Trying to get debug token for challenge %s (retries remaining %s)" % (challenge, numTries)
            fd = urllib2.urlopen("%s?key=%s" % (url, challenge) )
            time.sleep(0.5)
            responses = fd.readlines()
            response = ''.join(responses)
            exp = re.compile(".*<td><pre>(.*)</pre>.*")
            m = exp.search(response)
            if m:
                return m.group(1)
            print numTries
        except Exception, e:
            #print "Exception %s seen while trying to fetch root debug token" % e
            pass
        time.sleep(delay)

def getpasswd(token):
    url = "http://git.insieme.local/cgi-bin/generateRootPassword.py"
    if not isurlreachable(url):
        url = "http://10.160.1.12:11011/cgi-bin/generateRootPassword.py"
        if not isurlreachable(url):
            #print "git.insieme.local is not reachable, neither is 10.160.1.12:11011"
            #print "Looks like DMZ zone. Create a ssh tunnel between git.insieme.local and this host"
            #print "Example:i On a system in cisco network run the following commands"
            #print "    ssh -R 0.0.0.0:11011:172.23.137.25:80  -p 112 -N -f dmz@173.36.240.158"
            #print "(GatewayPorts should be set to yes in sshd config of dmz jumpserver)"
            return "printmessage"
    passwd = generateToken(token, url)
    return passwd

