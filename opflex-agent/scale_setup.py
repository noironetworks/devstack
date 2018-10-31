from optparse import OptionParser
import json
from string import Template
import os
import logging
from logging.handlers import RotatingFileHandler
import subprocess
import sys
import re


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

    def isBridgePresent(self, bridge):
       ret = subprocess.Popen( "brctl" + " show " +  bridge, shell=True, stdout=subprocess.PIPE)
       for line in ret.stdout:
          if bridge in line:
             return bool(re.search('No such device', line))
           
    def setupBridge(self, bridge):
       if not self.isBridgePresent(bridge):
          try:
             status = subprocess.call( "brctl" + " addbr " + bridge, shell=True, stdout=subprocess.PIPE) 
          except OSError as e:
             logger.error("bridge creation failed\n" + e)
             raise

    def createLink(self, name_space):
       pass



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
    
        


