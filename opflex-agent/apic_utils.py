import json
import requests
import urllib3
import logging
import sys

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
try:
    from requests.packages.urllib3.exceptions import InsecureRequestWarning
    requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
except Exception:
    pass



class Apic(object):
    def __init__(self, addr, user, passwd, name, ssl=True):
        self.addr = addr
        self.ssl = ssl
        self.user = user
        self.passwd = passwd
        self.cookies = None
        self.login()
        self.max_secgrp_index = 0
        self.logger = logging.getLogger(name)

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
        req = requests.post(self.url(path), data=data, cookies=self.cookies, verify=False)
        if req.status_code != requests.codes.ok:
           self.logger.error(req.text)
        else:
           return req

    def delete(self, path):
        req = requests.delete(self.url(path), cookies=self.cookies, verify=False)
        if req.status_code != requests.codes.ok:
           self.logger.error(req.text)
        else:
           return req


