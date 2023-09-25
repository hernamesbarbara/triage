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

def linkedin_command():
    lt = LinkedinTriage()
    try:
        print(lt.triage(args['INPUT'], how='copy', overwrites='skip'), file=sys.stdout)
    except Exception as e:
        print(e, file=sys.stderr)

def list_commands():
    
    valid_commands = {
        'linkedin': linkedin_command,
        'list': list_commands
    }
    
    print(os.linesep.join(valid_commands.keys()), file=sys.stdout)

if __name__ == "__main__":
    # INPUT = sys.argv[1:][0]
    # how = 'copy'
    # overwrites = 'skip'
    # lt = LinkedinTriage()

    # lt.triage(INPUT, how=how, overwrites=overwrites)

    args = docopt(__doc__)
    if args.get('list'):
        list_commands()
    elif args.get('linkedin'):
        linkedin_command()
    else:
        print(f"Unknown command", file=sys.stderr)