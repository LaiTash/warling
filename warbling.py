__author__ = 'Lai Tash (lai.tash@yandex.ru)'

from wboperations import opcodes
import machine
import argparse
import os
import sys

parser = argparse.ArgumentParser(description="Standalone interpreter for Mount&Blade scripts")

parser.add_argument(
    '-m',
    '--entry',
    action='store',
    dest='entry_point',
    type=str,
    metavar = '<entry point>',
    default = 'main',
    help = "set the initial script to execute (default 'main')"
)

parser.add_argument(
    '--scripts',
    action='store',
    dest='scripts_list_name',
    type=str,
    default = 'scripts'
)

parser.add_argument(
    '-e',
    '--execute',
    action='store',
    dest='execute_filename',
    help = 'execute file',
    metavar = '<filename>'
)

parser.add_argument(
    '-a',
    action='store',
    type= int,
    dest = 'arguments',
    nargs='*',
    default=[]
)

args = parser.parse_args()
dct = {}

if args.execute_filename is not None:
    if not (os.path.exists(args.execute_filename) and os.path.isfile(args.execute_filename)):
        print "file not found: %s" % args.execute_filename
        exit(1)
    source = open(args.execute_filename, 'r').read()
    py_compiled = compile(source, args.execute_filename, 'exec')
    exec(py_compiled) in dct
    if not args.scripts_list_name in dct:
        print "'%s' not found in %s" % (args.scripts_list_name, args.execute_filename)
        exit(1)
    interpreter = machine.WBMachine(dct[args.scripts_list_name], opcodes)
    interpreter.execute_script_by_name(args.entry_point, args.arguments)
else:
    parser.print_help()
