#!/usr/bin/env python3
import os
import sys
from clients import LinkedinTriage

if __name__ == "__main__":
    INPUT = sys.argv[1:][0]
    how = 'copy'
    overwrites = 'skip'
    lt = LinkedinTriage()

    lt.triage(INPUT, how=how, overwrites=overwrites)