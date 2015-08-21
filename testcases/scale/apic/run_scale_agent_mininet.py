import time
import subprocess
import sys
from multiprocessing import Process
from random import randrange

opflex_config_dir_base = "/etc/opflex-agent-ovs/"

def agent(id):

	id_str = str(id)

	if id < 256:
		id_hex_str = format(id, '02x')
	else:
		id_hex_str = format(id - 256, '02x')

	opflex_config_dir = opflex_config_dir_base + id_str

	# create the folder
	subprocess.Popen(["mkdir", "-p", opflex_config_dir])

	# make sure directory is created
	time.sleep(1)
	
	# drop the config file
	
	conf_content = '{"log":{"level":"debug2"}, "opflex":{"domain":"comp/prov-OpenStack/ctrlr-[openstack]-openstack/sw-InsiemeLSOid", "name":"example-agent' + id_str + '", "peers":[{"hostname":"172.23.137.40", "port":"8009"}], "ssl":{"mode":"enabled", "ca-store":"/etc/ssl/certs/"}, "inspector":{"enabled": true, "socket-name": "/etc/opflex-agent-ovs/' + id_str + '/opflex-agent-ovs-inspect.sock"}}, "endpoint-sources":{"filesystem":["/etc/opflex-agent-ovs/' + id_str + '"]}, "renderers":{"stitched-mode":{"ovs-bridge-name":"br-int", "encap":{"vxlan":{"encap-iface":"br-int_vxlan0", "uplink-iface":"eth1.4093", "uplink-vlan":4093, "remote-ip":"10.0.0.32", "remote-port": 8472}}, "forwarding":{"virtual-router":{"enabled":true, "mac":"00:22:bd:f8:19:ff", "ipv6":{"router-advertisement":"false"}}, "virtual-dhcp":{"enabled":"true", "mac":"00:22:bd:f8:19:ff"}}, "flowid-cache-dir": "/etc/opflex-agent-ovs/' + id_str + '"}}}'

	conf_file_name = opflex_config_dir + '/opflex-agent-ovs.conf'
	f = open(conf_file_name, 'w')
	f.write(conf_content)
	f.close()

	log_file_name = opflex_config_dir + '/agent.log'	

	# start the agent under its own network namespace

	#subprocess.Popen(["agent_ovs", "-c", conf_file_name])
	subprocess.Popen(["agent_ovs", "-c", conf_file_name, "--log", log_file_name])

	for outer_iteration in range(0, 10):
		for iteration in range(1, 11):

			index = outer_iteration*10 + iteration
			index_hex_str = format(index, '02x')

			# EPG number is from 1 to 35
			EPG_index = randrange(1, 36)

			tenant_index = id % 10
			tenant_index = tenant_index*10 + iteration

			# drop EPs

			if id < 256:
				ep_content = '{"interface-name": "veth6", "ip": ["192.168.' + id_str + '.' + str(index) + '"], "promiscuous-mode": false, "mac": "36:8c:97:ff:' + id_hex_str + ':' + index_hex_str + '", "policy-space-name": "yeah' + str(tenant_index) + '", "attributes": {"vm-name": "kent vm"}, "endpoint-group-name": "noiro|canHazEpg' + str(EPG_index) + '", "uuid": "1649307c-e335-47a1-b3d1-6b425bec' + id_hex_str + index_hex_str + '"}'
			else:
				ep_content = '{"interface-name": "veth6", "ip": ["192.100.' + str(id - 256) + '.' + str(index) + '"], "promiscuous-mode": false, "mac": "36:8c:99:ff:' + id_hex_str + ':' + index_hex_str + '", "policy-space-name": "yeah' + str(tenant_index) + '", "attributes": {"vm-name": "kent vm"}, "endpoint-group-name": "noiro|canHazEpg' + str(EPG_index) + '", "uuid": "1649307c-e335-99a1-b3d1-6b425bec' + id_hex_str + index_hex_str + '"}'

			ep_file_name = opflex_config_dir + '/' + str(index) + '.ep'
			f = open(ep_file_name, 'w')
			f.write(ep_content)
			f.close()

		time.sleep(5)

if __name__ == '__main__':
	for x in range(0, int(sys.argv[1])):
		p = Process(target=agent, args=(x,))
		p.start()
		time.sleep(5)

	p.join()





