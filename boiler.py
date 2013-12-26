#!/usr/bin/python

import argparse
import os
import shutil
import sys


class _BoilerArgumentsException(Exception):
    pass

def _raiseBoilerArgumentsException(*args, **kwargs):
    raise _BoilerArgumentsException

class Boiler(object):
    def __init__(self):
        self.templates_dir = os.path.join(os.environ['HOME'], '.boiler')
        self.output_dir = os.curdir
        self.stderr = sys.stderr
        self.template_list = []
        self._arg_parser = None

    def apply_boilerplate(self, name):
        template_path = os.path.join(self.templates_dir, name)
        output_path = os.path.join(self.output_dir, name)
        shutil.copyfile(template_path, output_path)
    
    def main(self, args):
        if not (self.parse_arguments(args) and self.template_list):
            self.print_usage()
        for template in self.template_list:
            self.apply_boilerplate(template)
    
    def _get_arg_parser(self):
        if not self._arg_parser:
            parser = argparse.ArgumentParser()
            parser.add_argument('--templates-dir',
                dest='templates_dir', action='store', metavar='DIR',
                help='Look for templates in DIR')
            parser.add_argument('--output-dir',
                dest='output_dir', action='store', metavar='DIR',
                help='Copy boilerplate into DIR')
            parser.add_argument('template',
                nargs='*',
                help='The template(s) to copy')
            parser.error = _raiseBoilerArgumentsException
            self._arg_parser = parser
        return self._arg_parser

    def print_usage(self):
        self._get_arg_parser().print_usage(self.stderr)
        sys.exit(2)

    def parse_arguments(self, args):
        try:
            args = self._get_arg_parser().parse_args(args)
        except _BoilerArgumentsException:
            return False
        if args.templates_dir:
            self.templates_dir = args.templates_dir
        if args.output_dir:
            self.output_dir = args.output_dir
        self.template_list = args.template
        return True


if __name__ == '__main__':
    Boiler().main(sys.argv[1:])

