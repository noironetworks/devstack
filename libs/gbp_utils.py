#!/usr/bin/env python
import sys, time
import paramiko
import subprocess
import re
import os
import sys
import json
import requests
import itertools
from prettytable import PrettyTable
from Crypto.PublicKey import RSA
from raise_exceptions import *

def sshClient(hostname, user, passwd,scp=0,file_name=''):
    sshclient = paramiko.SSHClient()
    sshclient.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        sshclient.connect(hostname, username=user, password=passwd)
    except Exception, e:
        raise ErrorConnectingToServer("Error connecting to server %s: %s" % (hostname, e))
        sshclient = None
    if scp!=0:
       _scp=SCPClient(sshclient.get_transport())
       try:
          _scp.put()
       except Exception, e:
           raise ErrorCoyFilesToServer("Error copying files from the server %s: %s" %(hostname, e))
           return None
    return sshclient


def report_table(suite_name):
    ps = subprocess.Popen(['grep', '-r', 'TESTCASE', '/tmp/%s.log' %(suite_name)], stdout=subprocess.PIPE)
    output = ps.communicate()[0]
    #print output
    output = output.splitlines()
    line = 0
    tc_dict = {}
    while line < len(output):
        find1 = re.search('\\b(TESTCASE_GBP_.*)\\b: (.*)' , output[line], re.I)
        if find1 != None:
           line += 1
           if line <= len(output) - 1:
              find2 = re.search('\\b%s\\b: (.*)' %(find1.group(1)), output[line],re.I)
              if find2 != None:
                 tc_dict[find1.group(1)]=find2.group(1), find1.group(2)
        line += 1
    #print tc_dict
    table = PrettyTable(["TESTCASE_ID", "RESULTS", "TESTCASE_HEADER"])
    table.padding_width = 1
    for key,val in tc_dict.iteritems():
        table.add_row(["%s" %(key),"%s" %(val[0]),"%s" %(val[1])])
    return table

def report_results(suite_name,txt_file):
    orig_stdout = sys.stdout
    f = open('%s' %(txt_file),'a')
    sys.stdout = f
    report=report_table(suite_name)
    print report
    sys.stdout = orig_stdout
    f.close()

def gen_tc_header():
    comb_list = [['same_leaf','two_leafs'],['same_host','two_hosts'],['same_ptg','two_ptgs'],\
                  ['same_L3_subnet','two_L3_subnets'],['same_L2_bd','two_L2_bds']]

    out_hdr_list=list(itertools.product(*comb_list))
    out_headers = []
    for hdr in out_hdr_list:
        header = 'test_'+'_'.join(str(i) for i in hdr)
        out_headers.append(header)
    #proto = map(list,list(itertools.combinations(['icmp','tcp','udp','dhcp','arp'],2)))
    proto = list(itertools.combinations(['icmp','tcp','udp','dhcp','arp'],2))
    proto_hdrs = []
    for hdr in proto:
        proto_header = '_'.join(str(i) for i in hdr)
        proto_hdrs.append(proto_header)
    in_hdrs = list(itertools.product(out_headers,proto_hdrs))
    final_headers = []
    for hdr in in_hdrs:
        tc_header = '_'.join(str(i) for i in hdr)
        final_headers.append(tc_header)
    table = PrettyTable(["TESTCASE_ID", "STATUS", "TESTCASE_HEADER"])
    table.padding_width = 1
    for i in range(len(final_headers)):
        table.add_row(["TESTCASE_DP_%s" %(i+1),"TBA","%s" %(final_headers[i])])
    print table
#tc_gen= gen_tc_header()

def gen_ssh_key(keyname): #TODO
    key = RSA.generate(2048)
    with open("~/%s_private.key" %(keyname), 'w') as keyfile:
         chmod("~/%s_private.key" %(keyname), 0600)
         keyfile.write(key.exportKey('PEM'))
    pubkey = key.publickey()
    with open("~/%s_public.pub" %(keyname), 'w') as keyfile:
         keyfile.write(pubkey.exportKey('OpenSSH'))
    pubkeypath="~/%s_public.pub" %(keyname)  
    return pubkeypath
     

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
        #return 'http://%s%s' % (self.addr, path)

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

def create_add_filter(apic_ip,svc_epg,username='admin',password='noir0123',tenant='_noirolab_admin'):
        """
        svc_epg: Preferably pass a list of svc_epgs if more than one
        """
        apic = Apic(apic_ip,username,password)

        #Create the noiro-ssh filter with ssh & rev-ssh subjects

        path = '/api/node/mo/uni/tn-%s/flt-noiro-ssh.json' %(tenant)
        data = '{"vzFilter":{"attributes":{"dn":"uni/tn-%s/flt-noiro-ssh","name":"noiro-ssh","rn":"flt-noiro-ssh","status":"created"},"children":[{"vzEntry":{"attributes":{"dn":"uni/tn-%s/flt-noiro-ssh/e-ssh","name":"ssh","etherT":"ip","prot":"tcp","sFromPort":"22","sToPort":"22","rn":"e-ssh","status":"created"},"children":[]}},{"vzEntry":{"attributes":{"dn":"uni/tn-%s/flt-noiro-ssh/e-ssh-rev","name":"ssh-rev","etherT":"ip","prot":"tcp","dFromPort":"22","dToPort":"22","rn":"e-ssh-rev","status":"created"},"children":[]}}]}}' %(tenant,tenant,tenant)
        req = apic.post(path, data)
        print req.text

        # Add the noiro-ssh filter to every svc_epg_contract
        if not isinstance(svc_epg,list):
           svc_epg = [svc_epg]
        for epg in svc_epg:
            path = '/api/node/mo/uni/tn-%s/brc-Svc-%s/subj-Svc-%s.json' %(tenant,epg,epg)
            data = '{"vzRsSubjFiltAtt":{"attributes":{"tnVzFilterName":"noiro-ssh","status":"created"},"children":[]}}'
            req = apic.post(path, data)
            print req.text
