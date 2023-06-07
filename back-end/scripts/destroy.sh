#!/bin/bash
set -xe

source ./export-env-variables.sh

read -p "Are you sure (yes/no)? " answer
case "$answer" in
    yes|YES|Yes )
        aws cloudformation delete-stack --stack-name sandbox-authe-${SUFFIX}
        aws cloudformation wait stack-delete-complete --stack-name sandbox-authe-${SUFFIX}
    ;;
esac
