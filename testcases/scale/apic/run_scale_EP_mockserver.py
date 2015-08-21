import time
import subprocess
import sys
from multiprocessing import Process

opflex_EP_dir = "/etc/opflex-agent-ovs/kent_mockserver"

def agent():

	# start the agent
	subprocess.Popen(["agent_ovs"])

	for outer_iteration in range(0, 256):

		outer_iteration_hex_str = format(outer_iteration, '02x')
		for iteration in range(1, 11):

			index = outer_iteration*10 + iteration
			iteration_hex_str = format(iteration, '02x')

			# drop EPs

			ep_content = '{"interface-name": "veth6", "ip": ["10.0.' + str(iteration) + '.' + str(outer_iteration) + '"], "promiscuous-mode": false, "mac": "36:8c:97:ff:' + iteration_hex_str + ':' + outer_iteration_hex_str + '", "policy-space-name": "test", "endpoint-group-name": "group1", "uuid": "1649307c-e335-47a1-b3d1-6b425bec' + iteration_hex_str + outer_iteration_hex_str + '"}'

			ep_file_name = opflex_EP_dir + '/' + str(index) + '.ep'
			f = open(ep_file_name, 'w')
			f.write(ep_content)
			f.close()

		time.sleep(1)

if __name__ == '__main__':
	p = Process(target=agent)
	p.start()

	p.join()





