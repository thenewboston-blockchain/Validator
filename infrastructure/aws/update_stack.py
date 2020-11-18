#!/usr/bin/env python3
import argparse
from secrets import token_urlsafe
import subprocess
from typing import TYPE_CHECKING
from urllib.parse import urlparse

import boto3
from thenewboston.argparser.validators import int_validator, str_length_validator, url_validator
from thenewboston.constants.network import BLOCK_IDENTIFIER_LENGTH, CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR, \
    VERIFY_KEY_LENGTH

if TYPE_CHECKING:
    from mypy_boto3_ssm.client import SSMClient
else:
    SSMClient = object


def main():
    ssm_client: SSMClient = boto3.client('ssm')

    p = argparse.ArgumentParser(description='AWS provision and deploy.')
    p.add_argument('--env', default='prod', type=str,
                   help='Environment to run, default is prod.')
    p.add_argument('--s3-bucket', required=True, type=str,
                   help='The name of the S3 bucket where this command uploads the artifacts that are referenced in '
                        'the template.')
    p.add_argument('--sign-key', required=True, type=str_length_validator(length=64),
                   help='Network sign key.')
    p.add_argument('--db-pass', type=str_length_validator(min_len=8),
                   help='Database password to set.')
    p.add_argument('--sentry-dsn', type=url_validator(),
                   help='DSN to set up Sentry tracking')

    p.add_argument('--node-type', choices=[CONFIRMATION_VALIDATOR, PRIMARY_VALIDATOR], default=CONFIRMATION_VALIDATOR,
                   help='Network standardized type of node, default: CONFIRMATION_VALIDATOR.')
    p.add_argument('--primary-url', type=url_validator(),
                   help='Primary validator URL (ex. http://10.10.10.10).')
    p.add_argument('--primary-trust', type=int_validator(),
                   help='Trust level for the validator.')

    p.add_argument('--node-identifier', required=True, type=str_length_validator(length=VERIFY_KEY_LENGTH),
                   help='Public key used to sign requests to other nodes.')
    p.add_argument('--account-number', required=True, type=str_length_validator(length=VERIFY_KEY_LENGTH),
                   help='The account number where Tx fees will be sent.')
    p.add_argument('--default-transaction-fee', required=True, type=int,
                   help='Tx fee cost.')
    p.add_argument('--seed-block-identifier', type=str_length_validator(length=BLOCK_IDENTIFIER_LENGTH),
                   help='Identifier of the last block that was used when the root account file was generated.')
    p.add_argument('--root-account-file', required=True, type=url_validator(suffix='.json'),
                   help='Record of all account balances at the moment in time that the validator was first set to '
                        '"primary".')
    p.add_argument('--version-number', required=True, type=str_length_validator(max_len=32),
                   help='API version.')

    args = p.parse_args()

    if args.node_type == CONFIRMATION_VALIDATOR and not args.primary_url:
        p.error('--primary-url is required when --node-type is CONFIRMATION_VALIDATOR.')

    if args.node_type == CONFIRMATION_VALIDATOR and not args.primary_trust:
        p.error('--primary-trust is required when --node-type is CONFIRMATION_VALIDATOR.')

    db_pass = args.db_pass
    if not db_pass:
        db_pass = token_urlsafe(32)

    deploy_args = [
        f'ParameterKey=EnvironmentName,ParameterValue={args.env.capitalize()}',
        f'ParameterKey=MasterUserPassword,ParameterValue={db_pass}',
        f'ParameterKey=NetworkSigningKey,ParameterValue={args.sign_key}',

        f'ParameterKey=NodeType,ParameterValue={args.node_type}',

        f'ParameterKey=NodeIdentifier,ParameterValue={args.node_identifier}',
        f'ParameterKey=AccountNumber,ParameterValue={args.account_number}',
        f'ParameterKey=DefaultTransactionFee,ParameterValue={args.default_transaction_fee}',
        f'ParameterKey=RootAccountFile,ParameterValue={args.root_account_file}',
        f'ParameterKey=VersionNumber,ParameterValue={args.version_number}',
    ]
    if args.seed_block_identifier:
        deploy_args.append(
            f'ParameterKey=SeedBlockIdentifier,ParameterValue={args.seed_block_identifier}'
        )

    if args.node_type == CONFIRMATION_VALIDATOR:
        primary = urlparse(args.primary_url)
        deploy_args.extend([
            f'ParameterKey=PrimaryIp,ParameterValue={primary.hostname}',
            f'ParameterKey=PrimaryProto,ParameterValue={primary.scheme}',
            f'ParameterKey=PrimaryPort,ParameterValue={primary.port or 80}',

            f'ParameterKey=PrimaryTrust,ParameterValue={args.primary_trust}'
        ])

    if args.sentry_dsn:
        deploy_args.append(
            f'ParameterKey=DjangoSentryDSN,ParameterValue={args.sentry_dsn}'
        )

    try:
        secret_key = ssm_client.get_parameter(
            Name=f'{args.env.capitalize()}ValidatorDjangoSecretKey{args.node_type}')['Parameter']['Value']
        print(secret_key)
    except (ssm_client.exceptions.ParameterNotFound, ssm_client.exceptions.InvalidKeyId):
        secret_key = token_urlsafe(32)

    deploy_args.append(
        f'ParameterKey=DjangoSecretKey,ParameterValue={secret_key}'
    )
    print(deploy_args)
    exit(1)

    subprocess.call([
        'sam', 'package',
        '--template-file', 'stack/env.cfn.yaml',
        '--s3-bucket', args.s3_bucket,
        '--output-template-file', 'outputtemplate.yaml'
    ])

    subprocess.call([
        'sam', 'deploy',
        '--stack-name', f'{args.env.capitalize()}Validator{args.node_type}',
        '--template-file', 'outputtemplate.yaml',
        '--parameter-overrides',
        ' '.join(deploy_args),
        '--capabilities', 'CAPABILITY_AUTO_EXPAND', 'CAPABILITY_NAMED_IAM'
    ])


if __name__ == '__main__':
    main()
