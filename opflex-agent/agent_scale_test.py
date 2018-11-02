from optparse import OptionParser
import json
from string import Template
import os
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import sys
import re
from pybrctl import BridgeController
from subprocess import PIPE


class OpflexAgent:
    agent_conf = Template('{"log":{"level":"debug"}, \
"opflex":{"domain":"$domain", "name":"agent-$id_Str", \
"peers":[{"hostname":"10.0.0.30", "port":"8009"}], \
"ssl":{"mode":"encrypted", "ca-store":"/etc/ssl/certs/"}, \
"inspector":{"enabled": true, "socket-name": "/var/run/opflex-agent$id_Str-ovs-inspect.sock"}, \
"notif":{"enabled": true, "socket-name": "/var/run/opflex-agent$id_Str-ovs-notif.sock", "socket-group": "opflexep", "socket-permissions": "770"}}, \
"endpoint-sources":{"filesystem":["/etc/opflex-agent-ovs/$id_Str"], "model-local": ["default"]}, \
"service-sources":{"filesystem":["/var/lib/opflex-agent-ovs/services"]}, \
"renderers":{}}')
    def __init__(self, options):
        self.agent_id = options["id"]
        self.config = self.agent_conf.substitute(domain = options["domain"], id_Str = options["id"])
        self.config_file_name = 'agent' + str(self.agent_id) + '_config_ovs.conf'
        self.base_dir = options["base_dir"]
        self.logger = options["logger"]

    def run(self):
        # setup config file
        path_to_conf_file = self.base_dir + '/' + self.config_file_name
        try:
            f = open(path_to_conf_file, 'w')
            f.write(self.config)
        except:
            self.logger.error("Unable to open or write to %s", path_to_config_file)
            raise
        finally:
            f.close()
           
        log_file = './agent' + str(self.agent_id) +  '.log'
        # start agent under its owm namespace
        try:
           subprocess.Popen(["sudo", "ip", "netns", "exec", "ns" + str(self.agent_id), "opflex_agent", "-c", path_to_conf_file, "--log", log_file])
        except Exception as ex:
           logger.error( type(ex))
           logger.error( sys.exc_info()[0])
           raise


class NetworkSetup:
    def __init__(self, interface):
       self.interface = interface
       self.brctl = BridgeController()
       

    def isBridgePresent(self, bridge):
       for br in self.brctl.showall():
          if 'br-agent'  in str(br):
            return True
       return False

           
    def setupBridge(self, bridge):
       self.bridge = bridge
       if not self.isBridgePresent(bridge):
          try:
             br = self.brctl.addbr("br-agent")
             br.addif(self.interface)
          except OSError as e:
             logger.error("bridge creation failed\n" + e)
             raise

    def createLink(self, name_space, idx):
       try:
          subprocess.call("ip link add " + name_space + "-tap" + " type veth peer name tap", shell=True)
          
          mac = "00:01:00:00:00:" + format(idx, '02x')
          subprocess.call("ip link set dev tap addr " + mac, shell=True)
          subprocess.call("ip link set tap netns " + name_space, shell=True)
          subprocess.call("brctl addif " + self.bridge + " " + name_space + "-tap", shell=True)
       except:
          logger.error("Unable to create link to namspace " + name_space)
          raise
       self.runDhclient(name_space, mac)

    def runDhclient(self, name_space, mac):
       # generate dhclient config from template.
       dhclient_config_tmplt = Template('option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;\n \
option ms-classless-static-routes code 249 = array of unsigned integer 8;\n \
option wpad code 252 = string;\n \
interface "tap" {\n \
\t\t\t\tsend host-name agent-$ns;\n \
\t\t\t\tsend dhcp-client-identifier 01:$mac_addr;\n}\n')
       dhclient_config = dhclient_config_tmplt.substitute( ns = name_space, mac_addr = mac )      
       # config file needs to be in /etc/dhcp as dhclient executable cannot read any other location.
       path_to_dhclient_file = '/etc/dhcp/dhclient-' + name_space + '.conf'
       try:
          f = open(path_to_dhclient_file, 'w')
          f.write(dhclient_config)
       except:
          self.logger.error("Unable to write to config file " + path_to_dhclient_file + '\n' + sys.exc_info()[0])
          raise
       finally:
          f.close()
       # run dhclient to get ip lease
       try:
          p = subprocess.Popen("ip netns exec " +  name_space + " dhclient" " -cf " + path_to_dhclient_file + " -lf /var/lib/dhclient/dhclient-" + name_space + ".lease" + " -pf /var/run/dhclient-" + name_space + " tap" , shell=True, stdout=PIPE, stderr=PIPE)
       except:
          self.logger.error("Error starting DHCP client for " + name_space + '\n stdout:\n' + p.stdout + '\n stderr:\n' + p.stderr)
          raise

 
if __name__ == '__main__':
    # setup logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    handler = RotatingFileHandler('agent_test.log', maxBytes=(1024*1024), backupCount=10)
    logger.addHandler(handler)

    logger.info("Running opflex agent scale test")

    parser = OptionParser()
    parser.add_option("-c", "--config", dest="config_file",
                      help="config file for scale setup")
    (options, args) = parser.parse_args()

    if options.config_file == None:
       parser.error("need config file")

    with open(options.config_file) as json_file:
       data = json.load(json_file)
       
    logger.info("options passed %s", json.dumps(data, indent=4))

    # setup bridge
    nw = NetworkSetup( data["interface"] )
    nw.setupBridge( "br-agent" )

    # setup base dir for agent
    base_dir = '/etc/opflex_agent'
    if not os.path.exists(base_dir):
       try:
         os.mkdir(base_dir)
       except:
         logger.error("cannot create %s", base_dir)
         raise

    # setup the agent spawning loop
    for id in range(data["num_agents"]):
        # create namespace and connect to bridge
        try:
            subprocess.call( "ip" + " netns" + " add" + " ns" + str(id+1), shell=True, stdout=subprocess.PIPE)
        except:
            e = sys.exc_info()[0]
            logger.error("bridge creation failed\n" + e)
            raise
        # create links between namspace and bridge
        nw.createLink("ns" + str(id+1), id+1)

        # setup listener socket dir for this agent
        socket_dir = '/etc/opflex-agent-ovs/' + str(id)
        if not os.path.exists(socket_dir):
           try:
             os.mkdir(socket_dir)
           except:
             logger.error("cannot create %s", socket_dir)
             raise
        # setup a dict of options and pass to agent
        agent_options = { "domain": data["domain"], "id" : id + 1, "base_dir": data["base_dir"], "logger": logger }
        agent = OpflexAgent(agent_options)
        agent.run()
    
        


