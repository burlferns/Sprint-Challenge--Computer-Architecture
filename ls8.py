#!/usr/bin/env python3

"""Main."""

import sys
from cpu import *

cpu = CPU()


# Process file input & load program array
program = []
file1 = open(sys.argv[1], 'r') 
for line in file1: 
    command = line.split('#',1)
    if command[0] != '' and command[0] != '\n':
        program.append(int(command[0], 2))

file1.close() 

# for elem in program:
#     print(bin(elem))


cpu.load(program)
cpu.run()