import logging
import sys
import argparse
from ids_validator.validate.validate import validate
from pathlib import Path


def configure_argument_parser():
    # Management of input arguments
    parser = argparse.ArgumentParser(description='IDS validator')

    parser.add_argument('command', help='command to be executed')
    validator_group = parser.add_argument_group('Validator arguments')
    validator_group.add_argument('-u', '--uri', type=str, required=True, help="uri, or uris")

    validator_group.add_argument('-r', '--ruleset', type=str, required=True, help="path to custom ruleset")

    validator_group.add_argument('-e', '--extra-rule-dirs', type=str, default=[], help="path to custom ruleset")

    validator_group.add_argument('-g', '--generic', action='store_true')
    validator_group.add_argument('-d', '--debug', action='store_true')

    return parser


def main():
    parser = configure_argument_parser()
    args = parser.parse_args(sys.argv[1:])

    uri = args.uri
    ruleset = ['test_ruleset']

    extra_rule_dirs = [Path(args.extra_rule_dirs)] if args.extra_rule_dirs else []

    apply_generic = args.generic
    command = args.command

    print(f'RULESET: {ruleset}')
    print(f'EXTRA: {extra_rule_dirs}')
    if command.lower() == 'validate':
        results = validate(ruleset, uri, extra_rule_dirs, apply_generic)
        print(type(results))
        print(results)


if __name__ == '__main__':
    main()

'''
python main.py VALIDATE --uri "imas:mdsplus?user=/home/ITER/wasikj/public/imasdb;database=test;pulse=1;run=1;version=3" --ruleset "test_ruleset"

'''
