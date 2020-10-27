#!/usr/bin/env python
import argparse
import subprocess


def str_length_validator(length=None, min_length=None):
    def inner(value):
        if not isinstance(value, str):
            raise argparse.ArgumentTypeError('Expecting string')
        if length and not len(value) == length:
            raise argparse.ArgumentTypeError('String length should be exactly %s chars' % length)
        if min_length and not len(value) >= min_length:
            raise argparse.ArgumentTypeError('String length should be greater or equal to %s chars' % min_length)
        return value
    return inner


def main():
    p = argparse.ArgumentParser(description='AWS provision and deploy')
    p.add_argument('--env', default='prod', type=str, help='Environment to run, default is prod')
    p.add_argument('--primary', action='store_true', help='If set, will init as primary validator')
    p.add_argument('--s3-bucket', required=True, type=str, help='The name of the S3 bucket where this command uploads '
                                                                'the artifacts that are referenced in the template.')
    p.add_argument('--sign-key', required=True, type=str_length_validator(length=64), help='Network sign key')
    p.add_argument('--db-pass', required=True, type=str_length_validator(min_length=8), help='Database password to set')

    args = p.parse_args()

    subprocess.call([
        'sam', 'package',
        '--template-file', 'stack/env.cfn.yaml',
        '--s3-bucket', args.s3_bucket,
        '--output-template-file', 'outputtemplate.yaml'
    ])

    subprocess.call([
        'sam', 'deploy',
        '--stack-name', '%s-environment' % args.env,
        '--template-file', 'outputtemplate.yaml',
        '--parameter-overrides',
        ' '.join(['ParameterKey=EnvironmentName,ParameterValue=%s' % args.env,
                  'ParameterKey=MasterUserPassword,ParameterValue=%s' % args.db_pass,
                  'ParameterKey=NetworkSigningKey,ParameterValue=%s' % args.sign_key,
                  'ParameterKey=ValidatorType,ParameterValue=%s' % ('primary' if args.primary else 'confirmation',)
                  ]),
        '--capabilities', 'CAPABILITY_AUTO_EXPAND', 'CAPABILITY_NAMED_IAM'
    ])


if __name__ == '__main__':
    main()
