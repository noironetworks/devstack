import apic_utils as Apic
import sys
import requests
import subprocess
from subprocess import PIPE
from xml.etree import ElementTree
import json
import os

def getL2Ep(apic, addr, agent):
    path = 'https://%s/api/node/class/opflexpL2Ep.xml?query-target-filter=and(eq(opflexpL2Ep.containerName,"%s"))' % (addr, agent, )
    return getMoCount(path, apic, addr)

def getLocalL2Ep(agent_index):
    if not os.path.exists("/var/run/opflex_agent" + agent_index + "-ovs-inspect.sock"):
       return 0
    subprocess.call("gbp_inspect --socket /var/run/opflex_agent" + agent_index + "-ovs-inspect.sock -prq EpdrL2Discovered -t dump -o agent" + agent_index + ".json", shell=True)
    count = 0
    with open("agent%s.json" % agent_index) as gbp_file:
       data = json.load(gbp_file)
    for gbp_dict in data:
       if gbp_dict['subject'] == "EpdrL2Discovered":
          count = len(gbp_dict['children'])
    os.remove("agent%s.json" % agent_index)
    return count

def getMoCount(path, apic, addr):
    ret = requests.get(path, cookies=apic.cookies, verify=False)
    retTree = ElementTree.fromstring(ret.content)
    return retTree.get('totalCount')

if __name__ == '__main__':
    if len(sys.argv) < 4:
        print "Usage: %s <leaf-addr> <username> <password>" % (sys.argv[0], )
        sys.exit(0)
    addr, user, passwd = sys.argv[1:4]
    apic = Apic.Apic(addr, user, passwd, "agent12")
    # read the config file to get generated artifact count
    with open('scale_setup_config.json') as json_file:
       data = json.load(json_file)

    num_agents = data['num_agents']
    path = 'https://%s//api/node/class/opflexODev.xml?query-target-filter=and(wcard(opflexODev.hostName,"agent"))' % (addr, )
    print "opflexODev: %s" % (getMoCount(path, apic, addr), )
    TotL2EpCount = 0
    TotDiscL2EpCount = 0
    for i in range(1,num_agents+1):
        L2EpCount = getL2Ep(apic, addr, "agent"+str(i))
        TotL2EpCount += int(L2EpCount)
        DiscL2EpCount = getLocalL2Ep(str(i))
        TotDiscL2EpCount += int(DiscL2EpCount)
        print "agent:%s, opflexpL2Ep:%s, DiscoveredL2Ep:%s" % (str(i), L2EpCount, DiscL2EpCount)
    print "Total counts  opflexpL2Ep:%d, DiscoveredL2Ep:%d" % (TotL2EpCount, TotDiscL2EpCount)




