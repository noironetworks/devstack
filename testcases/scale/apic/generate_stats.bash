#!/bin/bash

START=$(($1))
END=$(($2))

while true
do
	for i in $(eval echo "{$START..$END}")
	do	
		arping -I "ep_if$i" 8.8.8.8 -c 1
	done
done
