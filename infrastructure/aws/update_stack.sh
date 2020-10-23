#!/bin/sh

sam package --template-file stack/env.cfn.yaml --s3-bucket thenewboston-stacks --output-template-file outputtemplate.yaml

sam deploy --stack-name prod-environment \
      --template-file outputtemplate.yaml \
      --parameter-overrides ParameterKey=EnvironmentName,ParameterValue=prod \
                   ParameterKey=MasterUserPassword,ParameterValue=thenewboston_password \
                   ParameterKey=NetworkSigningKey,ParameterValue=6f812a35643b55a77f71c3b722504fbc5918e83ec72965f7fd33865ed0be8f81 \
      --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
#
#sam deploy --stack-name dev-environment \
#      --template-file outputtemplate.yaml \
#      --parameter-overrides ParameterKey=EnvironmentName,ParameterValue=dev \
#                   ParameterKey=MasterUserPassword,ParameterValue=thenewboston_password \
#      --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
