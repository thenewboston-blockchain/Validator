#!/bin/sh

sam package --template-file env.yaml --s3-bucket thenewboston-stacks --output-template-file outputtemplate.yaml

sam deploy --stack-name prod-environment \
      --template-file outputtemplate.yaml \
      --parameter-overrides ParameterKey=EnvironmentName,ParameterValue=prod \
                   ParameterKey=MasterUserPassword,ParameterValue=thenewboston_password \
      --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
#
#sam deploy --stack-name dev-environment \
#      --template-file outputtemplate.yaml \
#      --parameter-overrides ParameterKey=EnvironmentName,ParameterValue=dev \
#                   ParameterKey=MasterUserPassword,ParameterValue=thenewboston_password \
#      --capabilities CAPABILITY_AUTO_EXPAND CAPABILITY_NAMED_IAM
