#!/usr/bin/env bash

# **demo.sh**
# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in demo.conf OPENSTACK_ENV_FILE var
# Usage:
# ./clean.sh

source demo.conf
source functions-common

# This script exits on an error so that errors don't compound and you see
# only the first error that occurred.
#set -o errexit

# Settings
# ========

set -o xtrace
source $OPENSTACK_ENV_FILE

if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD=$OS_PASSWORD
fi
if [ -z "$NON_ADMIN_PASSWORD" ]; then
    NON_ADMIN_PASSWORD=$OS_PASSWORD
fi

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME
delete_vms
delete_policy_targets
unset_prs_and_external_segments_for_external_policies
unset_external_segment_for_l3_policies
delete_external_segments
unset_prs_for_groups
if [ -n "`heat stack-show $ADMIN_STACK | grep 'id'`" ]; then
    heat stack-delete "$ADMIN_STACK"
    confirm_resource_deleted "heat stack-show" "$ADMIN_STACK"
fi
if [ -n "`heat stack-show $CONTRACTS_STACK | grep 'id'`" ]; then
    heat stack-delete "$CONTRACTS_STACK"
    confirm_resource_deleted "heat stack-show" "$CONTRACTS_STACK"
fi
delete_external_segments

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
