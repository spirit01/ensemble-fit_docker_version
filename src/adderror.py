#!/usr/bin/python3
# vim: cin:

import numpy as np
import re
import sys


def adderror(file1, file2):
    s = []
    err = []
    with open(file1, 'r') as inf:
        for line in inf:
            if not line.startswith('#'):
                f = re.split(r'\s+', line)
                if f[0] == '':
                    f = f[1:]
                s.append(float(f[0]))
                err.append(np.log(float(f[2]) / float(f[1])))

    pol = np.polyfit(s, err, 5)

    with open(file2, 'r') as inf:
        with open(file2 + '.modified.dat', 'w') as modified:
            for line in inf:
                if line.startswith('#'):
                    print("")
                else:
                    f = re.split(r'\s+', line)
                    if f[0] == '':
                        f = f[1:]
                    e = np.exp(np.polyval(pol, float(f[0]))) * float(f[1])
                    modified.write(
                        """{s1} \t {s2} \t {s3} \n""".format(s1=f[0], s2=np.random.normal(float(f[1]), e), s3=e))
    return file2 + ".modified.dat"


if __name__ == '__main__':
    adderror(sys.argv[1], sys.argv[2])
