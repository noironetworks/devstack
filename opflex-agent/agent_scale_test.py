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
import apic_request
import agent_scale_cleanup
import uuid


# loop around range counter
class RangeCounter:
    def __init__(self, args):
       self.start = args["start"]
       self.max = args["max"]
       self.current_index = self.start

    def next_index(self):
       if( self.current_index > self.max ):
           self.current_index = 1
       retval = self.current_index
       self.current_index += 1
       return retval

class OpflexAgent:
    """
    agent_conf = Template('{"log":{"level":"debug"}, \
"opflex":{"domain":"$domain", "name":"agent-$id_Str", \
"peers":[{"hostname":"10.0.0.30", "port":"8009"}], \
"ssl":{"mode":"encrypted", "ca-store":"/etc/ssl/certs/"}, \
"inspector":{"enabled": true, "socket-name": "/var/run/opflex_agent$id_Str-ovs-inspect.sock"}, \
"notif":{"enabled": true, "socket-name": "/var/run/opflex_agent$id_Str-ovs-notif.sock", "socket-group": "opflexep", "socket-permissions": "770"}}, \
"endpoint-sources":{"filesystem":["/etc/opflex_agent/$id_Str"], "model-local": ["default"]}, \
"service-sources":{"filesystem":["/etc/opflex_agent/services/$id_Str"]}, \
"renderers":{}, \
"simulate":{"enabled": true, "update-interval": 15 }}')
    """

    agent_conf = Template(' \
      {"log": { \
        "level": "debug" \
      }, \
      "opflex": { \
        "domain": "$domain", \
        "name": "agent-$id_Str", \
        "peers": [ \
          { \
            "hostname": "10.0.0.30", \
            "port": "8009" \
          } \
        ], \
        "ssl": { \
          "mode": "encrypted", \
          "ca-store": "/etc/ssl/certs/" \
        }, \
        "inspector": { \
          "enabled": true, \
          "socket-name": "/var/run/opflex_agent$id_Str-ovs-inspect.sock" \
        }, \
        "notif": { \
          "enabled": true, \
          "socket-name": "/var/run/opflex_agent$id_Str-ovs-notif.sock", \
          "socket-group": "opflexep", \
          "socket-permissions": "770" \
        } \
      }, \
      "endpoint-sources": { \
        "filesystem": [ \
          "/etc/opflex_agent/$id_Str" \
        ], \
        "model-local": [ \
          "default" \
        ] \
      }, \
      "service-sources": { \
        "filesystem": [ \
          "/etc/opflex_agent/services/$id_Str" \
        ] \
      }, \
      "renderers": {}, \
      "simulate": { \
        "enabled": true, \
        "update-interval": 15 \
      } \
    }') 
    #ep_content = Template('{"interface-name": "ep_if$index", "ip": ["192.168.$id_Str.$index"], "promiscuous-mode": false, "mac": "36:8c:97:ff:$id_hex_str:$index_hex_str", "policy-space-name": "$tenant", "attributes": {"vm-name": "agent$id_Str","org-id":"scale-test$id_Str"}, "endpoint-group-name": "$tenant|$tenant$EPG_index", "uuid": "1649307c-e335-47a1-b3d1-6b425bec$id_hex_str$index_hex_str"}')
    ep_content = Template(' \
    { \
      "interface-name": "ep_if$index", \
      "ip": [ \
        "192.168.$id_Str.$index" \
      ], \
      "promiscuous-mode": false, \
      "mac": "36:8c:97:ff:$id_hex_str:$index_hex_str", \
      "policy-space-name": "$tenant", \
      "attributes": { \
        "vm-name": "agent$id_Str", \
        "org-id": "scale-test$id_Str" \
      }, \
      "endpoint-group-name": "$tenant|$tenant$EPG_index", \
      "uuid": "$uuid", \
      "security-group": [ \
       { \
         "policy-space": "$tenant", \
         "name": "$SecGrp" \
       } \
      ] \
    }') 


    def __init__(self, options):
        self.agent_id = options["id"]
        self.config = self.agent_conf.substitute(domain = options["domain"], id_Str = options["id"])
        self.config_file_name = 'agent' + str(self.agent_id) + '_config_ovs.conf'
        self.base_dir = options["base_dir"]
        self.logger = options["logger"]
        self.tenant = options["tenant_name"]
        self.epg_start_index = options["start_epg_index"]
        self.epg_max_index = options["max_epg_index"]
        self.ep_per_agent = options["ep_per_agent"]

    def run(self, max_secgrp_index):
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
           
        # setup base dir for agent logs
        base_dir_logs = '/var/log/opflex_agent'
        if not os.path.exists(base_dir_logs):
          try:
             os.mkdir(base_dir_logs)
          except:
             logger.error("cannot create %s", base_dir_logs)
             raise

        log_file = base_dir_logs + '/agent' + str(self.agent_id) +  '.log'
        # create ep files directory
        path_to_ep_files = '/etc/opflex_agent/' + str(self.agent_id)
        if not os.path.exists( path_to_ep_files ):
           try:
              os.mkdir(path_to_ep_files)
           except:
              logger.error("cannot create ep file dir " + path_to_ep_files)
              sys.exit("cannot create ep file dir " + path_to_ep_files)
        # create services files directory
        services_dir = '/etc/opflex_agent/services'
        if not os.path.exists( services_dir ):
           try:
              os.mkdir(services_dir)
           except:
              logger.error("cannot create services dir " + services_dir)
              sys.exit("cannot create services dir " + path_to_ep_files)
        # create services directory for this agent
        path_to_svc_files = '/etc/opflex_agent/services/' + str(self.agent_id)
        if not os.path.exists( path_to_svc_files ):
           try:
              os.mkdir(path_to_svc_files)
           except:
              logger.error("cannot create svc file dir " + path_to_svc_files)
              sys.exit("cannot create svc file dir " + path_to_svc_files)
        # start agent under its own namespace
        try:
           subprocess.Popen(["sudo", "ip", "netns", "exec", "ns" + str(self.agent_id), "opflex_agent", "-c", path_to_conf_file, "--log", log_file])
        except Exception as ex:
           logger.error( type(ex))
           logger.error( sys.exc_info()[0])
           raise

        epg_range_counter = RangeCounter({"start": self.epg_start_index, "max": self.epg_max_index})
        # create end point files
        id_hex_str = format( self.agent_id, '02x' )
        secgrp_index = 1
        for ep_index in range(1, self.ep_per_agent+1):
            idx_hex_str = format( ep_index, '02x' )
            ep_config = self.ep_content.substitute( id_Str = self.agent_id, index = ep_index, id_hex_str = id_hex_str, \
                                                    index_hex_str = idx_hex_str, tenant = self.tenant, \
                                                    EPG_index = epg_range_counter.next_index(), uuid = uuid.uuid4(), \
                                                    SecGrp = self.tenant + "SecGrp" + str(secgrp_index)  )
            path_to_ep_file = path_to_ep_files + '/' + str(ep_index) + '.ep'
            try:
              f = open(path_to_ep_file, 'w')
              f.write(ep_config)
            except:
              self.logger.error("Unable to write EP file " + path_to_ep_file )
              sys.exit("Unable to write EP file " + path_to_ep_file)
            finally:
              f.close()
            secgrp_index += secgrp_index
            secgrp_index = ((secgrp_index - 1) % max_secgrp_index) + 1


class NetworkSetup:
    def __init__(self, interface):
       self.interface = interface
       self.brctl = BridgeController()
       

    def isBridgePresent(self, bridge):
       for br in self.brctl.showall():
          if bridge  in str(br):
            return True
       return False

           
    def setupBridge(self, bridge):
       if not self.isBridgePresent(bridge):
          try:
             br = self.brctl.addbr(bridge)
             br.addif(self.interface)
             self.bridge = br
          except OSError as e:
             logger.error("bridge creation failed\n" + e)
             raise

    def createLink(self, name_space, idx):
       try:
          # assume the bridge has been created and named 'br-agent'
          subprocess.call("ip link add " + name_space + "-tap" + " type veth peer name tap", shell=True)
          subprocess.call("ip link set dev " + name_space + "-tap" + " up", shell=True)
          
          mac = "00:0c:29:fc:2f:" + format(idx, '02x')
          subprocess.call("ip link set dev tap addr " + mac, shell=True)
          subprocess.call("ip link set tap netns " + name_space, shell=True)
          self.bridge.addif(name_space + "-tap")
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
          p = subprocess.Popen("ip netns exec " +  name_space + " dhclient" " -cf " + path_to_dhclient_file + " -lf /var/lib/dhcp/dhclient-" + name_space + ".leases" + " -pf /var/run/dhclient-" + name_space + " tap" , shell=True, stdout=PIPE, stderr=PIPE)
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
    parser.add_option("-d", "--cleanup", action="store_true", 
                      help="delete all artifacts generated as part of the test\non the agent host and APIC")
    (options, args) = parser.parse_args()

    if options.config_file == None:
       parser.error("need config file")

    with open(options.config_file) as json_file:
       data = json.load(json_file)
       
    logger.info("options passed %s", json.dumps(data, indent=4))

    # get the orchestration technology and VMM domain
    domain = data["domain"].split("/")
    domain_orch = domain[1].replace("prov-","")
    domain_vmm = domain[2].split("[")[1].split("]")[0]

    # provision APIC with the required artifacts
    args = { "apic_ip": data["apic_ip"], "apic_uid": data["apic_uid"], "apic_passwd": data["apic_passwd"], 
             "tenant_name": data["tenant_name"], "EPGs": data["total_epg"], "EPs": data["total_ep"], \
             "domain_orch": domain_orch, "domain_vmm": domain_vmm }
    if( options.cleanup == True ):
       apic = apic_request.delete_policy(args)
       agent_scale_cleanup.cleanup(logger)
       sys.exit(0)
    else:
       apic = apic_request.create_policy(args)
    
    # setup bridge
    nw = NetworkSetup( data["interface"] )
    nw.setupBridge( "br-agent" )

    # setup base dir for agent
    base_dir = data["base_dir"]
    if not os.path.exists(base_dir):
       try:
         os.mkdir(base_dir)
       except:
         logger.error("cannot create %s", base_dir)
         raise

    # how many end points per agent ? total EP/num agents
    ep_per_agent,leftover_eps = divmod(data["total_ep"],data["num_agents"])
    total_epgs = data["total_epg"]
    current_epg_index = 1
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
        socket_dir = '/etc/opflex-agent-ovs' 
        if not os.path.exists(socket_dir):
           try:
             os.mkdir(socket_dir)
           except:
             logger.error("cannot create %s", socket_dir)
             raise

        socket_dir = '/etc/opflex-agent-ovs/' + str(id)
        if not os.path.exists(socket_dir):
           try:
             os.mkdir(socket_dir)
           except:
             logger.error("cannot create %s", socket_dir)
             raise
        # setup a dict of options and pass to agent
        if leftover_eps > 0:
           ep_count = ep_per_agent + 1
           leftover_eps -= 1
        else:
           ep_count = ep_per_agent

        agent_options = { "domain": data["domain"], "id" : id + 1, "base_dir": data["base_dir"], "logger": logger, \
                          "tenant_name": data["tenant_name"], "ep_per_agent": ep_count, "start_epg_index": current_epg_index, \
                          "max_epg_index": total_epgs}
        agent = OpflexAgent(agent_options)
        agent.run(apic.max_secgrp_index)
 
           
        current_epg_index = ((current_epg_index  + ep_per_agent - 1) % total_epgs) + 1
    
        


