#!/bin/bash

pkill agent_ovs

START=0
END=$(($1))
for i in $(eval echo "{$START..$END}")
do	
	link_str="link$i"
	link_Str_1="${link_str}-1"
	ns_str="ns$i"

	echo "tearing down network namespace for agent$i"

	ip netns exec $ns_str ip link set dev $link_str down
	ip link set dev $link_Str_1 down
	ip link delete $link_Str_1
	#ip netns exec $ns_str ip link delete $link_str
	ip netns delete $ns_str
	#brctl delif testbr $link_Str_1

	ovs-vsctl del-br "br$i"
	ip link set dev "ep_if$i" down
	ip link del "ep_if$i"

	rm -rf "/etc/opflex-agent-ovs/$i"

	rm -rf "/etc/dhcp/${i}.conf"
	rm -rf "/var/lib/dhclient/dhclient--link${i}.lease"
	rm -rf "/var/run/dhclient-link${i}.pid"

	sleep 1
done

brctl delif testbr opflex1.4093
pkill dhclient












