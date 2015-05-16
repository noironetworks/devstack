#!/usr/bin/env bash

# **demo.sh**
# Prior to running this script check the following:
# 1. Set the name and path of the keystone_admin file in demo.conf OPENSTACK_ENV_FILE var
# ./add-tenant.sh


source demo.conf
source functions-common


echo "*********************************************************************"
echo "GBP demo setup: Adding tenants and roles"
echo "*********************************************************************"

# This script exits on an error so that errors don't compound and you see
# only the first error that occurred.
set -o errexit

# Settings
# ========

set -o xtrace
source $OPENSTACK_ENV_FILE

if [ -z "$ADMIN_PASSWORD" ]; then
    ADMIN_PASSWORD=$OS_PASSWORD
fi

set_user_password_tenant $ADMIN_USERNAME $ADMIN_PASSWORD $ADMIN_TENANT_NAME

TENANTS=($HR_TENANT_NAME $ENG_TENANT_NAME)
USERS=($ADMIN_USERNAME $NON_ADMIN_USERNAME)
ROLES=("heat_stack_owner" "_member_")

for tenant in "${TENANTS[@]}"
do
    keystone tenant-create --name $tenant --enabled true
    for user in "${USERS[@]}"
    do
        for role in "${ROLES[@]}"
        do
            keystone user-role-add --user $user --role $role --tenant $tenant
        done
    done
done

echo "*********************************************************************"
echo "SUCCESS: End $0"
echo "*********************************************************************"
