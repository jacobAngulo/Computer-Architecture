#!/usr/bin/env python3
# this file uses the cpu class built in a a separate file and runs it once it is ran

"""Main."""

import sys
from cpu import *

cpu = CPU()

cpu.load()
cpu.run()
