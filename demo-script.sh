#!/bin/bash

set -e
set -x

cd ${HOME}/devstack
. openrc admin demo

# setup
IMAGE=$(nova image-list | awk '/cirros-0.3.1-x86_64-uec\ / {print $2}' | head -1)

# create some genreally useful classifiers/actions
neutron policy-classifier-create --direction bi all
neutron policy-classifier-create --protocol tcp --port-range 80 --direction in http
neutron policy-classifier-create --protocol tcp --port-range 443 --direction in https
neutron policy-classifier-create --protocol tcp --port-range 22 --direction in ssh
neutron policy-action-create --action-type allow allow

# create web-contract
neutron policy-rule-create --classifier http --action allow allow-http
neutron policy-rule-create --classifier https --action allow allow-https
neutron contract-create --policy-rules "allow-http allow-https" web-contract

# create EPGs for providers and consumers
neutron endpoint-group-create --provided-contracts web-contract=None web-epg
neutron endpoint-group-create --consumed-contracts web-contract=None client-epg

# now use them
# create a web server
neutron endpoint-create --endpoint-group web-epg web-server-ep-1
PORT=$(neutron endpoint-list -c neutron_port_id -c name | awk '/web-server-ep-1 / {print $2}' | head -1)
nova boot --image ${IMAGE} --flavor m1.tiny --nic port-id=${PORT} web-server-1

# create a client for web server
neutron endpoint-create --endpoint-group client-epg client-ep-1
PORT=$(neutron endpoint-list -c neutron_port_id -c name | awk '/client-ep-1 / {print $2}' | head -1)
nova boot --image ${IMAGE} --flavor m1.tiny --nic port-id=${PORT} client-1

# create admin rule to inspect all traffic via the firewall
# first, create a FW 
neutron firewall-policy-create admin-fw-policy
neutron firewall-create --admin-state-down --name admin-fw admin-fw-policy
sleep 5

# now, use it to inspect all traffic
FWID=$(neutron firewall-list | awk '/admin-fw / {print $2}' | head -1)
neutron policy-action-create --action-type redirect --action-value ${FWID} redirect-to-fw
neutron policy-rule-create --classifier all --action redirect-to-fw redirect-to-fw
neutron contract-create --policy-rules "redirect-to-fw" --child-contracts web-contract admin-contract

# update the web contract to allow SSH in addition to HTTP and HTTPS
neutron policy-rule-create --classifier ssh --action allow allow-ssh
neutron contract-update --policy-rules "allow-http allow-https allow-ssh" web-contract
