#!/bin/sh


# to be run with NCPU == NMODELS

#### specific parameters

# expecting modNN.pdb and saxs.dat here
data=/storage/brno3-cerit/home/ljocha/foxs

maxq=.5

####

cat - >$data/param <<EOF
foxs=/storage/brno3-cerit/home/ljocha/soft/foxs/foxs
parsemap=/storage/brno3-cerit/home/ljocha/soft/foxs/parse-map
data=$data
maxq=$maxq
measured=saxs.dat
EOF

loopwe=/storage/brno3-cerit/home/ljocha/soft/foxs/loop-we.sh

pbsdsh $loopwe $data/param
