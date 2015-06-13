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

set_user_password_tenant $NON_ADMIN_USERNAME $NON_ADMIN_PASSWORD $HR_TENANT_NAME
unset_prs_for_groups
sleep 5
delete_vms
delete_policy_targets
if [ -n "`heat stack-show $HR_STACK | grep 'id'`" ]; then
    heat stack-delete "$HR_STACK"
    confirm_resource_deleted "heat stack-show" "$HR_STACK"
fi

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
