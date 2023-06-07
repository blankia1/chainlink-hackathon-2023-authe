#!/bin/bash
set -ex

export region="us-west-2"
export region_alias="pdx"

source ./export-env-variables.sh

cd ../

swagger-merger -i swagger.yml -o swagger.generated.yml

sam build

sam deploy --parameter-overrides "$(cat .sam-envs/sandbox-$region_alias | tr '\n' ' ') Version=1.0 Suffix=${SUFFIX}" --no-fail-on-empty-changeset --region $region --s3-bucket sandbox-$region_alias-202492706836-sam-deployments --stack-name $STACK --s3-prefix $STACK --capabilities CAPABILITY_NAMED_IAM CAPABILITY_AUTO_EXPAND

cd -