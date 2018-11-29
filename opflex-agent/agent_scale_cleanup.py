import subprocess
from subprocess import Popen, PIPE
import shlex
from time import sleep
from pybrctl import BridgeController
import glob
import time


def cleanup(logger, num_agents):
    """
    list1 = subprocess.Popen(["ps", "-ef"], stdout=PIPE)
    list3 = subprocess.Popen(["grep", "-v", "grep"], stdin=list1.stdout, stdout=PIPE)
    list2 = subprocess.Popen(["grep", "opflex"], stdin=list3.stdout, stdout=PIPE)
    proc_list = list2.communicate()   
    proc_list = proc_list[0].strip().split('\n')
    for line in proc_list:
       tokens = shlex.split(line)
       if tokens[7].count('sudo') == 1:
          cmd = ["pkill", " -P ", tokens[1]]
          subprocess.Popen(cmd, stdout=PIPE)
    """
    # delete all endpoint files first so agent can undeclare them causing the leaf to clean them up.
    logger.info("deleting generated files under /etc/opflex_agent")
    kill = subprocess.Popen(["rm", "-Rf", "/etc/opflex_agent"], stdout=PIPE)        
    # wait for the undeclare to the leaf so the leaf cleans up endpoints.
    sleep_time = (num_agents/10 + 1) * 5
    logger.info("sleeping " + str(sleep_time) + " seconds to wait for EP cleanup.... ")
    time.sleep(sleep_time)
    kill = subprocess.Popen(["pkill", "opflex"], stdout=PIPE)        
    kill = subprocess.Popen(["pkill", "-f", "dhclient-ns"], stdout=PIPE)        
    files = glob.glob('etc/dhcp/dhclient-ns*')
    for file in files:
       kill = subprocess.call(["rm", "-Rf", file] )        
    files = glob.glob('/var/lib/dhcp/dhclient-ns*')
    for file in files:
       kill = subprocess.call(["rm", "-Rf", file])        
    files = glob.glob('/var/run/opflex_agent*-ovs-notif.sock')
    for file in files:
       kill = subprocess.call(["rm", "-Rf", file])
    kill = subprocess.Popen(["rm", "-Rf", "/var/log/opflex_agent"], stdout=PIPE)        
    name_spaces = subprocess.Popen(["ls", "/var/run/netns"], stdout=PIPE)
    # get a list of all namespaces. Assumption: all namespaces follow this format - ns#
    # delete all ip links. Assumption - all links connecting the name spaces follow this naming scheme - ns#-tap
    # the above links connect the name space to the linux bridge "br-agent".
    # del interface from br-agent that connects to the fabric.
    # delete all namspace links and then delete the brodge.
    # delete all namspaces created as part of this test.
    try:
      br = BridgeController().getbr("br-agent")
      for intfc in br.getifs():
        br.delif(intfc)
        if str(intfc).find("ns") != -1:
          subprocess.Popen(["ip", "link", "set", "dev", str(intfc), "down"], stdout=PIPE)
          subprocess.Popen(["ip", "link", "del", str(intfc)], stdout=PIPE)
      BridgeController().delbr("br-agent")
    except:
      pass
    subprocess.Popen(["ip", "-all", "netns", "delete"], stdout=PIPE)
#    ns_list = name_spaces.communicate()[0].strip().split('\n')
#    for ns in ns_list:
#       print ns 

