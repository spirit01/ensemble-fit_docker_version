#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import pathlib

# pathlib.Path('.'+'/files').mkdir(parents=True, exist_ok=True)
name = ''
with open('final.pdb') as file:
    for line in file:
        if line.startswith('MODEL'):
            name = line.split()[1]
            with open(name + '.pdb') as file2:
                file2.write(line)
                if line.startswith('ENDMDL'):
                    break
