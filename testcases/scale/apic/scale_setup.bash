#!/bin/bash

brctl addbr testbr
brctl addif testbr opflex1.4093
ip link set testbr up
echo 256 > /proc/sys/fs/inotify/max_user_instances

START=0
END=$(($1))
for i in $(eval echo "{$START..$END}")
do	
	link_str="link$i"
	link_Str_1="${link_str}-1"
	ns_str="ns$i"
	
	echo "setting up network namespace for agent$i"

	ip link add $link_Str_1 type veth peer name $link_str

	printf -v hex_i "%02x" "$i"
	identifier="00:01:00:00:00:$hex_i"

	if [ $i -gt 255 ]
	then
		j=`expr $i - 256`
		printf -v hex_i "%02x" "$j"		
		identifier="00:02:00:00:00:$hex_i"
	fi

	ip link set dev $link_str addr $identifier
	brctl addif testbr $link_Str_1

	ip netns add $ns_str
	ip link set dev $link_str netns $ns_str

	ip link set dev $link_Str_1 up
	ip netns exec $ns_str ip link set dev $link_str up

	echo "setting up OVS bridge for agent$i"

	ovs-vsctl add-br "br$i"
	ovs-vsctl add-port "br$i" "br-int_br$i" -- set Interface "br-int_br$i" type=vxlan options:remote_ip=flow options:key=flow
	
	# create a pair interface
	ip link add "ep_if$i" type veth peer name "ep_if${i}-1"
	ip link set dev "ep_if$i" up	
	ip link set dev "ep_if${i}-1" up

	ovs-vsctl add-port "br$i" "ep_if$i"

	echo "acquiring dhcp IP"

	if [ -e "/etc/dhcp/${i}.conf" ]; then
		echo 'File "/etc/dhcp/${i}.conf" already exists!'
	else
		cat <<- EOF >> "/etc/dhcp/${i}.conf"
		send dhcp-client-identifier 01:${identifier};
		request subnet-mask, domain-name, domain-name-servers, host-name;
		send host-name example-agent${i};

		option rfc3442-classless-static-routes code 121 = array of unsigned integer 8;
		option ms-classless-static-routes code 249 = array of unsigned integer 8;
		option wpad code 252 = string;

		also request rfc3442-classless-static-routes;
		also request ms-classless-static-routes;
		also request static-routes;
		also request wpad;
		also request ntp-servers;
		EOF
	fi

	ip netns exec $ns_str /sbin/dhclient -v -H "example-agent$i" -q -cf "/etc/dhcp/${i}.conf" -lf "/var/lib/dhclient/dhclient--link${i}.lease" -pf "/var/run/dhclient-link${i}.pid" $link_str
done

pkill dhclient
