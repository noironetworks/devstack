import json
import requests

class Apic(object):
    def __init__(self, addr, user, passwd, ssl=True):
        self.addr = addr
        self.ssl = ssl
        self.user = user
        self.passwd = passwd
        self.cookies = None
        self.login()

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

def create_policy():

	apic = Apic('172.23.137.40:8000', 'admin', 'ins3965!', False)
	#apic = Apic('172.28.184.80', 'admin', 'noir0123')    

	# play with infra tenant

	path = '/api/node/mo/uni/infra.json'

	#data = '{"infraInfra":{"attributes":{"dn":"uni/infra","status":"created,modified"},"children":[{"infraAccPortP":{"attributes":{"dn":"uni/infra/accportprof-Switch101_Profile_ifselector","name":"Switch101_Profile_ifselector","descr":"GUI Interface Selector Generated PortP Profile: Switch101_Profile","status":"created,modified"},"children":[{"infraHPortS":{"attributes":{"dn":"uni/infra/accportprof-Switch101_Profile_ifselector/hports-assPortSelector-typ-range","name":"assPortSelector","type":"range","status":"created,modified"},"children":[{"infraPortBlk":{"attributes":{"dn":"uni/infra/accportprof-Switch101_Profile_ifselector/hports-assPortSelector-typ-range/portblk-block1","fromPort":"20","toPort":"40","name":"block1","status":"created,modified","rn":"portblk-block1"},"children":[]}},{"infraRsAccBaseGrp":{"attributes":{"tDn":"uni/infra/funcprof/accportgrp-assPortSelector_PolGrp","status":"created,modified"},"children":[]}}]}}]}},{"infraFuncP":{"attributes":{"dn":"uni/infra/funcprof","status":"modified"},"children":[{"infraAccPortGrp":{"attributes":{"dn":"uni/infra/funcprof/accportgrp-assPortSelector_PolGrp","name":"assPortSelector_PolGrp","status":"created"},"children":[]}}]}},{"infraNodeP":{"attributes":{"dn":"uni/infra/nprof-Switch101_Profile","name":"Switch101_Profile","descr":"GUI Interface Selector Generated Profile: Switch101_Profile","status":"created,modified"},"children":[{"infraLeafS":{"attributes":{"dn":"uni/infra/nprof-Switch101_Profile/leaves-Switch101_Profile_selector_101-typ-range","name":"Switch101_Profile_selector_101","type":"range","status":"created"},"children":[{"infraNodeBlk":{"attributes":{"dn":"uni/infra/nprof-Switch101_Profile/leaves-Switch101_Profile_selector_101-typ-range/nodeblk-single0","status":"created","from_":"101","to_":"101","name":"single0","rn":"nodeblk-single0"},"children":[]}}]}},{"infraRsAccPortP":{"attributes":{"tDn":"uni/infra/accportprof-Switch101_Profile_ifselector","status":"created,modified"},"children":[]}}]}}]}}'
	#req = apic.post(path, data)
	#print req.text

	data = '{"infraInfra":{"attributes":{"dn":"uni/infra","status":"modified"},"children":[{"infraAttEntityP":{"attributes":{"dn":"uni/infra/attentp-assAccEntProf","name":"assAccEntProf","rn":"attentp-assAccEntProf","status":"created"},"children":[{"infraProvAcc":{"attributes":{"dn":"uni/infra/attentp-assAccEntProf/provacc","status":"created"},"children":[]}}]}},{"infraFuncP":{"attributes":{"dn":"uni/infra/funcprof","status":"modified"},"children":[]}}]}}'

	req = apic.post(path, data)
	print req.text

	# create mcast pool

	path = '/api/node/mo/uni/infra/maddrns-noiro-mcast.json'
	data = '{"fvnsMcastAddrInstP":{"attributes":{"dn":"uni/infra/maddrns-noiro-mcast","name":"noiro-mcast","rn":"maddrns-noiro-mcast","status":"created"},"children":[{"fvnsMcastAddrBlk":{"attributes":{"dn":"uni/infra/maddrns-noiro-mcast/fromaddr-[225.1.1.1]-toaddr-[225.1.15.255]","from":"225.1.1.1","to":"225.1.15.255","rn":"fromaddr-[225.1.1.1]-toaddr-[225.1.15.255]","status":"created"},"children":[]}}]}}'
	req = apic.post(path, data)
	print req.text

	# OpenStack VxLAN NS ADD

	path = '/api/node/mo/uni.xml'
	data = '<polUni> \
				<infraInfra> \
					<fvnsVxlanInstP name="openstack-vxlan1"> \
						<fvnsEncapBlk name="encap" from="vxlan-960000" to="vxlan-990000"/> \
					</fvnsVxlanInstP> \
				</infraInfra> \
			</polUni>'
	req = apic.post(path, data)
	print req.text

	# openstack vmm

	path = '/api/node/mo/uni.xml'
	data = '<vmmProvP vendor="OpenStack"> \
    			<vmmDomP name="openstack" enfPref="sw" encapMode="vxlan" mcastAddr="225.1.16.1" mode="ovs"> \
       				<vmmUsrAccP dn="uni/vmmp-OpenStack/dom-openstack/usracc-openstack1" name="openstack1" usr="noiro" pwd="noiro" rn="usracc-openstack1" status="created"> \
       				</vmmUsrAccP> \
       				<vmmCtrlrP \
            			name="openstack" scope="openstack" rootContName="openstack" hostOrIp="192.168.65.154" mode="ovs"> \
            			<vmmRsVxlanNs tDn="uni/infra/vxlanns-openstack-vxlan1"/> \
       				</vmmCtrlrP> \
       				<vmmRsDomMcastAddrNs tDn="uni/infra/maddrns-noiro-mcast"/> \
   				</vmmDomP> \
			</vmmProvP>'
	req = apic.post(path, data)
	print req.text

	# Attach AEP to openstack domain

	path = '/api/node/mo/uni/infra/attentp-assAccEntProf.json'
	data = '{"infraRsDomP":{"attributes":{"tDn":"uni/vmmp-OpenStack/dom-openstack","status":"created,modified"},"children":[]}}'
	req = apic.post(path, data)
	print req.text

	# Associate creds to VMM domain

	path = '/api/node/mo/uni/vmmp-OpenStack/dom-openstack/ctrlr-openstack/rsacc.json'
	data = '{"vmmRsAcc":{"attributes":{"tDn":"uni/vmmp-OpenStack/dom-openstack/usracc-openstack1","status":"created"},"children":[]}}'
	req = apic.post(path, data)
	print req.text

	# 100 tenants

	for i in range(1, 101):

		print '-----------------------------------configure tenant' + str(i) + '------------------------------------------------------'

		if i % 20 == 0:
			print '-------------------log in again to avoid time-out---------------------'
			apic.login()

		i_hex_str = format(i, '02x')

		# add tenant   

		path = '/api/node/mo/uni/tn-yeah' + str(i) + '.json'
		data = '{"fvTenant":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '","name":"yeah' + str(i) + '","rn":"tn-yeah' + str(i) + '","status":"created"}, "children":[{"fvCtx":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/ctx-assNet","name":"assNet","rn":"ctx-assNet","status":"created"},"children":[]}}]}}'
		req = apic.post(path, data)
		print req.text
	
		# add app profile

		path = '/api/node/mo/uni/tn-yeah' + str(i) + '/ap-noiro.json'
		data = '{"fvAp":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/ap-noiro","name":"noiro","rn":"ap-noiro","status":"created"}}}'
		req = apic.post(path, data)
		print req.text

		# 40 contracts each tenant

		for index in range(1, 41):

			# add contract

			path = '/api/node/mo/uni/tn-yeah' + str(i) + '/brc-assContract' + str(index) + '.json'
			data = '{"vzBrCP":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/brc-assContract' + str(index) + '","name":"assContract' + str(index) + '","rn":"brc-assContract' + str(index) + '","status":"created"},"children":[{"vzSubj":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/brc-assContract' + str(index) + '/subj-assSubject","name":"assSubject","rn":"subj-assSubject","status":"created"},"children":[{"vzRsSubjFiltAtt":{"attributes":{"status":"created","tnVzFilterName":"icmp"},"children":[]}}]}}]}}'
			req = apic.post(path, data)
			print req.text
	
		# 35 EPGs/BDs each tenant

		for index in range(1, 36):

			# add a BD
	
			index_hex_str = format(index, '02x')

			path = '/api/node/mo/uni/tn-yeah' + str(i) + '/BD-assBd' + str(index) + '.json'
			data = '{"fvBD":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/BD-assBd' + str(index) + '","mac":"00:22:BD:F8:' + i_hex_str + ':' + index_hex_str + '","name":"assBd' + str(index) + '","rn":"BD-assBd' + str(index) + '","status":"created"},"children":[{"dhcpLbl":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/BD-assBd' + str(index) + '/dhcplbl-default","name":"default","rn":"dhcplbl-default","status":"created"},"children":[{"dhcpRsDhcpOptionPol":{"attributes":{"tnDhcpOptionPolName":"default","status":"created,modified"},"children":[]}}]}},{"fvRsCtx":{"attributes":{"tnFvCtxName":"assNet","status":"created,modified"},"children":[]}},{"fvSubnet":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/BD-assBd' + str(index) + '/subnet-[172.' + str(i) + '.' + str(index) + '.1/24]","ip":"172.' + str(i) + '.' + str(index) + '.1/24","rn":"subnet-[172.' + str(i) + '.' + str(index) + '.1/24]","status":"created"}}}]}}'
			req = apic.post(path, data)
			print req.text

			# add an EPG

			path = '/api/node/mo/uni/tn-yeah' + str(i) + '/ap-noiro/epg-canHazEpg' + str(index) + '.json'

			data = '{"fvAEPg":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/ap-noiro/epg-canHazEpg'  + str(index) + '","name":"canHazEpg'  + str(index) + '","rn":"epg-canHazEpg'  + str(index) + '","status":"created"},"children":[{"fvRsBd":{"attributes":{"tnFvBDName":"assBd'  + str(index) + '","status":"created,modified"},"children":[]}}]}}'
			req = apic.post(path, data)
			print req.text

			# assign contract to EPG

			data = '{"fvAEPg":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '/ap-noiro/epg-canHazEpg'  + str(index) + '","status":"modified"}, \
							   "children":[{"fvRsCons":{"attributes":{"status":"created,modified","tnVzBrCPName":"assContract'  + str(index) + '"},"children":[]}}, \
										   {"fvRsProv":{"attributes":{"status":"created,modified","tnVzBrCPName":"assContract'  + str(index) + '"},"children":[]}}]}}'
			req = apic.post(path, data)
			print req.text

			# add VMM domain association to EPG

			data = '{"fvRsDomAtt":{"attributes":{"tDn":"uni/vmmp-OpenStack/dom-openstack","status":"created"},"children":[]}}'
			req = apic.post(path, data)
			print req.text


if __name__ == '__main__':
	create_policy()
