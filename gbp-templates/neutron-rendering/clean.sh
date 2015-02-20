#!/usr/bin/env bash

# Usage:
# ./clean.sh

source demo.conf
source functions-common

function unset_prs_for_groups {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    uuids="$(echo $(gbp group-list | get_field 1) | sed 's/id //g')"
    for id in $uuids
    do
        set -o xtrace
        gbp group-update $id --provided-policy-rule-sets ""
        gbp group-update $id --consumed-policy-rule-sets ""
        set +o xtrace
    done
    $xtrace
}

function unset_prs_and_external_segments_for_external_policies {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    uuids="$(echo $(gbp external-policy-list | get_field 1) | sed 's/id //g')"
    for id in $uuids
    do
        set -o xtrace
        gbp external-policy-update $id --provided-policy-rule-sets ""
        gbp external-policy-update $id --consumed-policy-rule-sets ""
        gbp external-policy-update $id --external-segments ""
        set +o xtrace
    done
    $xtrace
}

function unset_external_segment_for_l3_policies {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    uuids="$(echo $(gbp l3policy-list | get_field 1) | sed 's/id //g')"
    for id in $uuids
    do
        set -o xtrace
        gbp l3policy-update $id --external-segment ""
        set +o xtrace
    done
    $xtrace
}

function delete_external_segments {
    local xtrace=$(set +o | grep xtrace)
    set +o xtrace
    uuids="$(echo $(gbp external-segment-list | get_field 1) | sed 's/id //g')"
    for id in $uuids
    do
        set -o xtrace
        gbp external-segment-delete $id
        set +o xtrace
    done
    $xtrace
}

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
unset_prs_and_external_segments_for_external_policies
unset_external_segment_for_l3_policies
delete_external_segments

unset_prs_for_groups
if [ -n "`heat stack-show $APP_STACK | grep 'id'`" ]; then
    heat stack-delete "$APP_STACK"
    confirm_resource_deleted "heat stack-show" "$APP_STACK"
fi

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
