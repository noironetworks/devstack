import socket
import re
import ssl
import main_test
import time
from multiprocessing import Process

def recv_timeout(the_socket,timeout=1):

    #make socket non blocking
    the_socket.setblocking(0)
     
    #total data partwise in an array
    total_data=[];
    data='';
     
    #beginning time
    begin=time.time()
    while 1:
        #if you got some data, then break after timeout
        if total_data and time.time()-begin > timeout:
            break
         
        #if you got no data at all, wait a little longer, twice the timeout
        elif time.time()-begin > timeout*2:
            break
         
        #recv something
        try:
            data = the_socket.recv(8192)
            if data:
                total_data.append(data)
                #change the beginning time for measurement
                begin=time.time()
            else:
                #sleep for sometime to indicate a gap
                time.sleep(0.1)
        except:
            pass
     
    #join all parts to make final string
    return ''.join(total_data)

def agent(id):

	# leaf1 IP in mininet env.
	host = '192.168.10.101'

	# opflex port
	port = 8009

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host, port))

	if main_test.sslFlag == 1:
		s = ssl.wrap_socket(s, cert_reqs=ssl.CERT_NONE)

	# ["send_identity",1]

	json = '{"id":["send_identity",1],"method":"send_identity","params":[{"proto_version":"1.0","name":"example-agent-' + str(id + 256) + '","domain":"comp/prov-OpenStack/ctrlr-[openstack]-openstack/sw-InsiemeLSOid", "my_role":["policy_element"]}]}\0'
	res = s.send(json)
	data = recv_timeout(s)
	print data

	match = re.search('"result":{"name":.+"my_role":.+"domain":.+"peers":.+"role":.+"connectivity_info":', data)
	if match == None:
   	    assert False, 'Error could not find the good result object in the json ["send_identity",1] response'

	while True:

		# ["policy_resolve",2]

		json = '{"id":["policy_resolve",2],"method":"policy_resolve","params":[{"subject":"PlatformConfig","policy_uri":"/PolicyUniverse/PlatformConfig/comp%2fprov-OpenStack%2fctrlr-%5bopenstack%5d-openstack%2fsw-InsiemeLSOid/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",2] response'

		# ["endpoint_declare",3]

		hex_str = format(id, '02x')

		json = '{"id":["endpoint_declare",3],"method":"endpoint_declare","params":[{"endpoint":[{"subject":"GbpeVMEp","uri":"/GbpeVMUniverse/GbpeVMEp/1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '/","properties":[{"name":"uuid","data":"1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '"}],"children":[],"parent_subject":"GbpeVMUniverse","parent_uri":"/GbpeVMUniverse/","parent_relation":"GbpeVMEp"}],"prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{}', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["endpoint_declare",3] response'

		# ["policy_resolve",4]

		json = '{"id":["policy_resolve",4],"method":"policy_resolve","params":[{"subject":"GbpEpGroup","policy_uri":"/PolicyUniverse/PolicySpace/yeah/GbpEpGroup/noiro%7ccanHazEpg/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",4] response'

		# ["endpoint_declare",5]

		json = '{"id":["endpoint_declare",5],"method":"endpoint_declare","params":[{"endpoint":[{"subject":"GbpeTunnelEp","uri":"/GbpeTunnelEpUniverse/GbpeTunnelEp/300a9443-be74-42bc-a789-ee602f4f0f' + hex_str + '/","properties":[{"name":"uuid","data":"300a9443-be74-42bc-a789-ee602f4f0f' + hex_str + '"},{"name":"mac","data":"00:50:56:89:e5:' + hex_str + '"},{"name":"encapId","data":4093},{"name":"terminatorIp","data":"172.28.185.' + str(id) + '"},{"name":"encapType","data":"vlan"}],"children":[],"parent_subject":"GbpeTunnelEpUniverse","parent_uri":"/GbpeTunnelEpUniverse/","parent_relation":"GbpeTunnelEp"}],"prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{}', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["endpoint_declare",5] response'

		# ["policy_resolve",6]

		json = '{"id":["policy_resolve",6],"method":"policy_resolve","params":[{"subject":"GbpFloodDomain","policy_uri":"/PolicyUniverse/PolicySpace/yeah/GbpFloodDomain/BDassBd/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",6] response'

		# ["policy_resolve",7]

		json = '{"id":["policy_resolve",7],"method":"policy_resolve","params":[{"subject":"GbpContract","policy_uri":"/PolicyUniverse/PolicySpace/yeah/GbpContract/assContract/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",7] response'

		# ["policy_resolve",8]

		json = '{"id":["policy_resolve",8],"method":"policy_resolve","params":[{"subject":"GbpBridgeDomain","policy_uri":"/PolicyUniverse/PolicySpace/yeah/GbpBridgeDomain/assBd/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",8] response'

		# ["policy_resolve",9]

		json = '{"id":["policy_resolve",9],"method":"policy_resolve","params":[{"subject":"GbpAllowDenyAction","policy_uri":"/PolicyUniverse/PolicySpace/common/GbpAllowDenyAction/allow/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",9] response'

		# ["policy_resolve",10]

		json = '{"id":["policy_resolve",10],"method":"policy_resolve","params":[{"subject":"GbpeL24Classifier","policy_uri":"/PolicyUniverse/PolicySpace/common/GbpeL24Classifier/5%7c0%7cIPv6/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",10] response'

		# ["policy_resolve",11]

		json = '{"id":["policy_resolve",11],"method":"policy_resolve","params":[{"subject":"GbpeL24Classifier","policy_uri":"/PolicyUniverse/PolicySpace/common/GbpeL24Classifier/5%7c0%7cIPv4/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",11] response'

		# ["policy_resolve",12]

		json = '{"id":["policy_resolve",12],"method":"policy_resolve","params":[{"subject":"GbpRoutingDomain","policy_uri":"/PolicyUniverse/PolicySpace/yeah/GbpRoutingDomain/assNet/","prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{"policy":.+"subject":.+"uri":.+"properties":.+"name":.+"data":.+"parent_subject":.+"parent_uri":.+"parent_relation":.+"children":', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["policy_resolve",12] response'

		# ["endpoint_declare",13]

		json = '{"id":["endpoint_declare",13],"method":"endpoint_declare","params":[{"endpoint":[{"subject":"EprL3Ep","uri":"/EprL3Universe/EprL3Ep/%2fPolicyUniverse%2fPolicySpace%2fyeah%2fGbpRoutingDomain%2fassNet%2f/192.168.2.' + str(id) + '/","properties":[{"name":"uuid","data":"1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '"},{"name":"group","data":"/PolicyUniverse/PolicySpace/yeah/GbpEpGroup/noiro%7ccanHazEpg/"},{"name":"ip","data":"192.168.2.' + str(id) + '"},{"name":"context","data":"/PolicyUniverse/PolicySpace/yeah/GbpRoutingDomain/assNet/"},{"name":"mac","data":"36:8c:97:ff:46:' + hex_str + '"}],"children":[],"parent_subject":"EprL3Universe","parent_uri":"/EprL3Universe/","parent_relation":"EprL3Ep"}],"prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{}', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["endpoint_declare",13] response'

		# ["endpoint_declare",14]

		json = '{"id":["endpoint_declare",14],"method":"endpoint_declare","params":[{"endpoint":[{"subject":"EprL2Ep","uri":"/EprL2Universe/EprL2Ep/%2fPolicyUniverse%2fPolicySpace%2fyeah%2fGbpBridgeDomain%2fassBd%2f/36%3a8c%3a97%3aff%3a46%3a' + hex_str + '/","properties":[{"name":"vmName","data":"kent vm"},{"name":"uuid","data":"1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '"},{"name":"interfaceName","data":"veth0"},{"name":"group","data":"/PolicyUniverse/PolicySpace/yeah/GbpEpGroup/noiro%7ccanHazEpg/"},{"name":"mac","data":"36:8c:97:ff:46:' + hex_str + '"},{"name":"context","data":"/PolicyUniverse/PolicySpace/yeah/GbpBridgeDomain/assBd/"}],"children":[],"parent_subject":"EprL2Universe","parent_uri":"/EprL2Universe/","parent_relation":"EprL2Ep"}],"prr":3600}]}\0'
		res = s.send(json)
		data = recv_timeout(s)
		print data

		match = re.search('"result":{}', data)
		if match == None:
			assert False, 'Error could not find the good result object in the json ["endpoint_declare",14] response'

		# send state_report every 30 secs

		index = 15
		while True:

			json = '{"id":["state_report",' + str(index) + '],"method":"state_report","params":[{"observable":[{"subject":"GbpeEpCounter","uri":"/ObserverEpStatUniverse/GbpeEpCounter/1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '/","properties":[{"name":"txPackets","data":100869},{"name":"uuid","data":"1649307c-e335-47a1-b3d1-6b425becd9' + hex_str + '"},{"name":"txMulticast","data":0},{"name":"txDrop","data":0},{"name":"txUnicast","data":0},{"name":"txBytes","data":6774533},{"name":"txBroadcast","data":0},{"name":"rxPackets","data":194146},{"name":"rxDrop","data":0},{"name":"rxBytes","data":253096632},{"name":"rxUnicast","data":0},{"name":"rxBroadcast","data":0},{"name":"rxMulticast","data":0}],"children":[],"parent_subject":"ObserverEpStatUniverse","parent_uri":"/ObserverEpStatUniverse/","parent_relation":"GbpeEpCounter"}]}]}\0'
			res = s.send(json)
			data = recv_timeout(s)
			print data

			match = re.search('"result":{}', data)
			if match == None:
				assert False, 'Error could not find the good result object in the json ["state_report",X] response'

			index = index + 1
			time.sleep(15)

if __name__ == '__main__':
	for x in range(0, 256):
		p = Process(target=agent, args=(x,))
		p.start()
		time.sleep(10)

	p.join()






















