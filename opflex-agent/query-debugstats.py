import json
import requests
import sys
from xml.etree import ElementTree


class Api(object):
    def __init__(self, addr, user, passwd, ssl=True, debug=False):
        self.ignore_warnings()
        self.debug = debug
        self.addr = addr
        self.user = user
        self.passwd = passwd
        token = self.login('api')
        self.cookies = {'APIC-Cookie': token}

    def ignore_warnings(self):
        try:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            from requests.packages import urllib3 as urllibr
            urllibr.disable_warnings(urllibr.exceptions.InsecureRequestWarning)
        except Exception:
            pass

    def login(self, api):
        data = '{"aaaUser":{"attributes":{"name": "%s", "pwd": "%s"}}}' % (
            self.user, self.passwd)
        path = 'https://%s/%s/aaaLogin.json' % (self.addr, api)
        ret = requests.post(path, data=data, verify=False)
        resp = self.get_resp(ret)
        token = None
        if resp:
            token = resp[0]["aaaLogin"]["attributes"]["token"]
        return token

    def getobj(self, path):
        path = 'https://%s/%s.json' % (self.addr, path)
        ret = requests.get(path, cookies=self.cookies, verify=False)
        return self.get_resp(ret)

    def get_resp(self, ret):
        if ret.status_code == 200:
            resp = json.loads(ret.text)
            return resp["imdata"]
        if self.debug:
            print ret, ret.text
        return None

    def get_debugobj(self, typ):
        resp = self.getobj('/api/opflexp/debug/%s' % (typ, ))
        return self.key_value_list(resp)

    def get_debug_data(self):
        debug_data_keys = [
            'configmocounters',
            'heapstats',
            'mitmocounters',
            'procstats',
        ]
        debug_data = dict(map(lambda x: (
            x, self.get_debugobj(x)), debug_data_keys))
        return debug_data

    @staticmethod
    def key_value_list(resp):
        return dict(map(lambda x: (
            x['KeyValue']['attributes']['key'],
            x['KeyValue']['children'][0]['Value']['attributes']['value']),
            resp[0]['KeyValueList']['children']))

    def getL2Ep(self, agent):
        path = 'https://%s/api/node/class/opflexpL2Ep.xml?query-target-filter=and(wcard(opflexpL2Ep.containerName,"%s"))' % (self.addr, agent, )
        ret = requests.get(path, cookies=self.cookies, verify=False)
        retTree = ElementTree.fromstring(ret.content)
        print "agent:%s, totalCount of opflexpL2Ep:%s" % (agent, retTree.get('totalCount'))

if __name__ == '__main__':
    dryrun = True
    if len(sys.argv) < 4:
        print "Usage: %s <leaf-addr> <username> <password>" % (sys.argv[0], )
    else:
        addr, user, passwd = sys.argv[1:4]
        api = Api(addr, user, passwd)
        debug_data = api.get_debug_data()
#        resp = api.getL2Ep("agent12")

        for key in sorted(debug_data.keys()):
            print '*****', key
            print json.dumps(debug_data[key], indent=4,
                             sort_keys=True, separators=(',', ': '))
