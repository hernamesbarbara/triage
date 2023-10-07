#!/usr/bin/env python3
"""triage - organize stuff quickly

Usage:
  triage list 
  triage linkedin INPUT
  triage -h | --help

Options:
  -h --help     Show this screen.

"""
import os
import sys
from clients.linkedintriage import LinkedinTriage
from docopt import docopt

__version__ = '0.0.1'

def linkedin_command():
    lt = LinkedinTriage()
    try:
        lt.triage(args['INPUT'], how='copy', overwrites='skip')
        return lt
    except Exception as e:
        print(e, file=sys.stderr)
        return lt

def list_commands():
    
    valid_commands = {
        'linkedin': linkedin_command,
        'list': list_commands
    }
    
    print(os.linesep.join(valid_commands.keys()), file=sys.stdout)

if __name__ == "__main__":
    args = docopt(__doc__, version=__version__)
    if args.get('list'):
        list_commands()
    elif args.get('linkedin'):
        lt = linkedin_command()
        print(f"Input: {args['INPUT']}", file=sys.stdout)
        print(lt.summary(), file=sys.stdout)
    else:
        print(f"Unknown command", file=sys.stderr)