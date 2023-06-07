#!/bin/bash
set -ex

timestamp=$(date +%s)

if [ ! -z "FORCE_DEPLOYMENT_SUFFIX" ]
then
    CURRENT_BRANCH=$CI_COMMIT_REF_NAME
    if [[ -z "${CURRENT_BRANCH}" ]]
    then
        CURRENT_BRANCH=$(git branch --show-current || echo $CI_COMMIT_BRANCH)
    fi

    SANDBOX_ID=$(echo $CURRENT_BRANCH | grep -oEi '[0-9]+' | head -1 | tr '[:upper:]' '[:lower:]')
    if [[ -z "${SANDBOX_ID}" ]]; then
      echo "No sandbox id"
    else
       export SUFFIX=-$SANDBOX_ID
    fi
else
    export SUFFIX=$FORCE_DEPLOYMENT_SUFFIX
fi

export PROJECT=sandbox-$region_alias-authe
export STACK=$PROJECT$SUFFIX
