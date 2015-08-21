import json
import requests
import time

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

def delete_policy():

	#apic = Apic('172.23.137.40:8000', 'admin', 'ins3965!', False)
	apic = Apic('172.28.184.80', 'admin', 'noir0123')    

	# 100 tenants

	for i in range(1, 101):

		print '-----------------------------------delete tenant' + str(i) + '------------------------------------------------------'

		if i % 20 == 0:
			print '-------------------log in again to avoid time-out---------------------'
			apic.login()

		# add tenant

		path = '/api/node/mo/uni/tn-yeah' + str(i) + '.json'
		data = '{"fvTenant":{"attributes":{"dn":"uni/tn-yeah' + str(i) + '","name":"yeah' + str(i) + '","rn":"tn-yeah' + str(i) + '","status":"deleted"}}}'
		req = apic.post(path, data)
		print req.text

                time.sleep(15) 
		
if __name__ == '__main__':
	delete_policy()
