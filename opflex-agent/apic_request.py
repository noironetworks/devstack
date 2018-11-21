import json
import requests
import sys

class Apic(object):
    def __init__(self, addr, user, passwd, ssl=True):
        self.addr = addr
        self.ssl = ssl
        self.user = user
        self.passwd = passwd
        self.cookies = None
        self.login()
        self.max_secgrp_index = 0

    def url(self, path):
        if self.ssl:
            return 'https://%s%s' % (self.addr, path)
        return 'http://%s%s' % (self.addr, path)

    def login(self):
        data = '{"aaaUser":{"attributes":{"name": "%s", "pwd": "%s"}}}' % (self.user, self.passwd)
        path = '/api/aaaLogin.json'
        req = requests.post(self.url(path), data=data, verify=False)
        if req.status_code == 200:
            resp = json.loads(req.text)
            token = resp["imdata"][0]["aaaLogin"]["attributes"]["token"]
            self.cookies = {'APIC-Cookie': token}
        return req

    def post(self, path, data):
        return requests.post(self.url(path), data=data, cookies=self.cookies, verify=False)
    def delete(self, path):
        return requests.delete(self.url(path), cookies=self.cookies, verify=False)

def create_policy(args):

	apic = Apic(args["apic_ip"], args["apic_uid"], args["apic_passwd"], True)

	# 100 tenants

	for i in range(1, 2):

		print '-----------------------------------configure tenant------------------------------------------------------'

		if i % 20 == 0:
			print '-------------------log in again to avoid time-out---------------------'
			apic.login()

		i_hex_str = format(i, '02x')

		# add tenant   
                tenant_name = args["tenant_name"]
		path = '/api/node/mo/uni/tn-' + tenant_name + '.json'
		data = '{"fvTenant":{"attributes":{"dn":"uni/tn-' + tenant_name + '","name":"' + tenant_name + '","rn":"tn-' + tenant_name + '","status":"created"}, "children":[{"fvCtx":{"attributes":{"dn":"uni/tn-' + tenant_name + '/ctx-' + tenant_name  + 'Net","name":"' + tenant_name + 'Net","rn":"ctx-' + tenant_name + 'Net","status":"created"},"children":[]}}]}}'
		req = apic.post(path, data)
		print req.text
		# add app profile

		path = '/api/node/mo/uni/tn-' + tenant_name + '/ap-' + tenant_name + '.json'
		data = '{"fvAp":{"attributes":{"dn":"uni/tn-' + tenant_name +'/ap-' + tenant_name +'","name":"' + tenant_name + '","rn":"ap-' \
                         + tenant_name + '","status":"created"}}}'
		req = apic.post(path, data)
		print req.text

		# contracts = specified in config file, otherwise one for every 5 EPGs.
                total_epgs = args["EPGs"]
                num_contracts = (total_epgs/5) + 1
                apic.max_secgrp_index = num_contracts

		for index in range(1, num_contracts +  1):

			# add contract

			path = '/api/node/mo/uni/tn-' + tenant_name + '/brc-' + tenant_name + 'Contract' + str(index) + '.json'
                        data = '{"vzBrCP": \
                                 {"attributes": \
                                  {"dn":"uni/tn-' + tenant_name + '/brc-' + tenant_name + 'Contract' + str(index) + \
                                   '","name":"' + tenant_name + 'Contract' + str(index) + \
                                   '","rn":"brc-' + tenant_name + 'Contract' + str(index) + \
                                   '","scope":"application-profile","status":"created"}, \
                                    "children":[ \
                                    {"vzSubj": \
                                     {"attributes": \
                                      {"dn":"uni/tn-' + tenant_name + '/brc-' + tenant_name + 'Contract' + str(index) + \
                                            '/subj-' + tenant_name + 'Subject", \
                                       "name":"' + tenant_name + 'Subject","rn":"subj-' + tenant_name + 'Subject","status":"created"}, \
                                       "children":[ \
                                        {"vzOutTerm": \
                                         {"attributes": \
                                          {"dn": "uni/tn-' + tenant_name + '/brc-' + tenant_name + 'Contract' + str(index) + \
                                            '/subj-' + tenant_name + 'Subject/outtmnl", \
                                            "status": "created"}, \
                                          "children":[ \
                                            {"vzRsFiltAtt": \
                                             {"attributes": \
                                              {"status":"created","tnVzFilterName":"icmp"}}}]}}, \
                                         {"vzInTerm": \
                                         {"attributes": \
                                          {"dn": "uni/tn-' + tenant_name + '/brc-' + tenant_name + 'Contract' + str(index) + \
                                            '/subj-' + tenant_name + 'Subject/intmnl", \
                                           "status": "created" }, \
                                          "children": \
                                          [{"vzRsFiltAtt": \
                                           {"attributes": \
                                            {"status":"created","tnVzFilterName":"icmp"}}}]}}]}}, \
                                    ]}}'
			req = apic.post(path, data)
			print req.text
	
                # add a security group
			path = '/api/node/mo/uni/tn-' + tenant_name + '/pol-' + tenant_name + 'SecGrp' + str(index) + '.json'
                        data = '{ \
                           "hostprotPol": { \
                             "attributes": { \
                               "descr": "Security Group", \
                               "dn": "uni/tn-' + tenant_name + '/pol-' + tenant_name + 'SecGrp' + str(index) + '", \
                               "name": "' + tenant_name + 'SecGrp' + str(index) + '" \
                             }, \
                             "children": [ \
                               { \
                                 "hostprotSubj": { \
                                   "attributes": { \
                                     "descr": "host prot subject", \
                                     "name": "' + tenant_name + 'Subj" \
                                   }, \
                                   "children": [ \
                                     { \
                                       "hostprotRule": { \
                                         "attributes": { \
                                           "descr": "host prot rule", \
                                           "direction": "egress", \
                                           "ethertype": "ipv4", \
                                           "name": "allow-all-egress" \
                                         }, \
                                       } \
                                     }, \
                                     { \
                                       "hostprotRule": { \
                                         "attributes": { \
                                           "direction": "ingress", \
                                           "ethertype": "ipv4", \
                                           "icmpCode": "7", \
                                           "connTrack": "normal", \
                                           "icmpType": "44", \
                                           "fromPort": "80", \
                                           "name": "allow-all-ingress", \
                                           "protocol": "unspecified", \
                                           "toPort": "80" \
                                         }, \
                                         "children": [ \
                                           { \
                                             "hostprotRemoteIp": { \
                                               "attributes": { \
                                                 "addr": "1.100.202.' + str(index) + '", \
                                                 "descr": "host prot rule", \
                                                 "name": "remote-IP" \
                                                  } \
                                                 } \
                                                } \
                                               ] \
                                             } \
                                           } \
                                         ] \
                                       } \
                                     } \
                                   ] \
                                 } \
                               }' 

			req = apic.post(path, data)
			print req.text

		# 35 EPGs/BDs each tenant

                contract_index = 1
		for index in range(1, total_epgs + 1):

			# add a BD
	
                        print " --------------   setup BD -----------------  "
			index_hex_str = format(index, '02x')
                        path = '/api/node/mo/uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '.json'
#			data = '{"fvBD":{"attributes":{"dn":"uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '","mac":"00:22:BD:F8:' + i_hex_str + ':' + index_hex_str + '","name":"' + tenant_name + 'Bd' + str(index) + '","rn":"BD-' + tenant_name + 'Bd' + str(index) + '","status":"created"},"children":[{"dhcpLbl":{"attributes":{"dn":"uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '/dhcplbl-default","name":"default","rn":"dhcplbl-default","status":"created"},"children":[{"dhcpRsDhcpOptionPol":{"attributes":{"tnDhcpOptionPolName":"default","status":"created,modified"},"children":[]}}]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"' + tenant_name + 'Net","status":"created,modified"},"children":[]}},{"fvSubnet":{"attributes":{"dn":"uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '/subnet-[172.' + str(i) + '.' + str(index) + '.1/24]","ip":"172.' + str(i) + '.' + str(index) + '.1/24","rn":"subnet-[172.' + str(i) + '.' + str(index) + '.1/24]","status":"created"}}}]}}'

                        data = '{ \
                          "fvBD": { \
                            "attributes": { \
                              "dn": "uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '", \
                              "mac": "00:22:BD:F8:' + i_hex_str + ':' + index_hex_str + '", \
                              "name": "' + tenant_name + 'Bd' + str(index) + '", \
                              "rn": "BD-' + tenant_name + 'Bd' + str(index) + '", \
                              "status": "created" \
                            }, \
                            "children": [ \
                              { \
                                "dhcpLbl": { \
                                  "attributes": { \
                                    "dn": "uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '/dhcplbl-default", \
                                    "name": "default", \
                                    "rn": "dhcplbl-default", \
                                    "status": "created" \
                                  }, \
                                  "children": [ \
                                    { \
                                      "dhcpRsDhcpOptionPol": { \
                                        "attributes": { \
                                          "tnDhcpOptionPolName": "default", \
                                          "status": "created,modified" \
                                        }, \
                                        "children": [] \
                                      } \
                                    } \
                                  ] \
                                } \
                              }, \
                              { \
                                "fvRsCtx": { \
                                  "attributes": { \
                                    "tnFvCtxName": "' + tenant_name + 'Net", \
                                    "status": "created,modified" \
                                  }, \
                                  "children": [] \
                                } \
                              }, \
                              { \
                                "fvSubnet": { \
                                  "attributes": { \
                                    "dn": "uni/tn-' + tenant_name + '/BD-' + tenant_name + 'Bd' + str(index) + '/subnet-[172.' + str(i) + '.' + str(index) + '.1/24]", \
                                    "ip": "172.' + str(i) + '.' + str(index) + '.1/24", \
                                    "rn": "subnet-[172.' + str(i) + '.' + str(index) + '.1/24]", \
                                    "status": "created" \
                                  } \
                                } \
                              } \
                            ] \
                          } \
                        }'

			req = apic.post(path, data)
			print req.text

			# add an EPG

			path = '/api/node/mo/uni/tn-' + tenant_name + '/ap-' + tenant_name + '/epg-' + tenant_name + '' + str(index) + '.json'

			data = '{"fvAEPg":{"attributes":{"dn":"uni/tn-' + tenant_name + '/ap-' + tenant_name + '/epg-' + tenant_name + ''  + str(index) + '","name":"' + tenant_name + ''  + str(index) + '","rn":"epg-' + tenant_name + ''  + str(index) + '","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"' + tenant_name + 'Bd'  + str(index) + '","status":"created,modified"},"children":[]}}]}}'
			req = apic.post(path, data)
			print req.text

			# assign contract to EPG

			data = '{"fvAEPg":{"attributes":{"dn":"uni/tn-' + tenant_name + '/ap-' + tenant_name + '/epg-' + tenant_name + ''  + str(index) + '","status":"modified"}, \
							   "children":[{"fvRsCons":{"attributes":{"status":"created,modified","tnVzBrCPName":"' + tenant_name + 'Contract'  + str(contract_index) + '"},"children":[]}}, \
										   {"fvRsProv":{"attributes":{"status":"created,modified","tnVzBrCPName":"' + tenant_name + 'Contract'  + str(contract_index) + '"},"children":[]}}]}}'
                        contract_index = (index/5) + 1
			req = apic.post(path, data)
			print req.text

			# add VMM domain association to EPG

			data = '{"fvRsDomAtt":{"attributes":{"tDn":"uni/vmmp-' + args["domain_orch"] + '/dom-' + args["domain_vmm"] + \
                               '","status":"created"},"children":[]}}'
			req = apic.post(path, data)
			print req.text
                return apic


def delete_policy(args):
    apic = Apic(args["apic_ip"], args["apic_uid"], args["apic_passwd"], True)

    tenant_name = args["tenant_name"]
    path = '/api/node/mo/uni/tn-' + tenant_name + '.json'
    req = apic.delete(path)
    print req.text

