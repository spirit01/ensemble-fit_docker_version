#!/usr/bin/python
# vim: cin:

import numpy as np
from scipy.optimize import curve_fit
import re
import sys

s = []
err = []

with open(sys.argv[1],'r') as inf:
	for line in inf:
		if not line.startswith('#'):
			f = re.split(r'\s+',line)
			if f[0] == '':
				f = f[1:]
			s.append(float(f[0]))
			err.append(np.log(float(f[2])/float(f[1])))
			
pol = np.polyfit(s,err,5)

print '# originally', sys.argv[2], ', randomized by errors learned from', sys.argv[1]
with open(sys.argv[2],'r') as inf:
	for line in inf:
		if line.startswith('#'):
			sys.stdout.write(line)
		else:
			f = re.split(r'\s+',line)
			if f[0] == '':
				f = f[1:]
			e = np.exp(np.polyval(pol,float(f[0]))) * float(f[1])
			print f[0], np.random.normal(float(f[1]),e), e
		
