#!/usr/bin/env python3

import sys

if len(sys.argv) != 2:
    print('File required!', file=sys.stderr)
    exit(1)

c1 = list()
c2 = list()
c3 = list()
with open(sys.argv[1]) as file:
	line = None
	for lineno, line in enumerate(file):
		if line and line != '\n' and not line.startswith('#'):
			try:
				v1, v2, v3 = line.strip().split()
				c1.append(float(v1))
				c2.append(float(v2))
				c3.append(float(v3))
			except ValueError:
				print('Incorrect values on line: ' + str(lineno + 1), file=sys.stderr)
				exit(2)

	if line is None or not (c1 and c2 and c3):
		print('File contains no data', file=sys.stderr)
		exit(2)
			
# Check that c1 is monotonous
if not all(x < y for x, y in zip(c1, c1[1:])):
	print('First column does not form a monotonous sequence.', file=sys.stderr)
	exit(2)

if not all(x > 0 for x in c2):
	print('Values in the second column are not always positive.', file=sys.stderr)
	exit(2)

if not all(x > 0 for x in c3):
	print('Values in the third column are not always positive.', file=sys.stderr)
	exit(2)

exit(0)