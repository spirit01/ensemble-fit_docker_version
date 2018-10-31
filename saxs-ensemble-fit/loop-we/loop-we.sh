#!/bin/sh

test $f "$1" || { echo "$1:" cannot source; exit 1; }
. $1

n=`printf %02d $(($PBS_VNODENUM + 1))`

# XXX: hardcoded


mkdir $SCRATCHDIR/$n
cd $SCRATCHDIR/$n
rm -f $n.out $n.err

feval()
{
	echo "$*" | bc -l
}

ftest()
{
	r=`echo "$*" | bc -l`
	test $r = 1
}

date >>$n.out

# XXX: specificka jmena souboru
cp $data/mod$n.pdb .
cp $data/$measured .

e=0.95

while ftest "$e <= 1.05"; do
	w=-2
	while ftest "$w <= 4"; do
		echo '***' $foxs -q $maxq -w $w -e $e mod$n.pdb $measured >>$n.out 
		echo '***' $foxs -q $maxq -w $w -e $e mod$n.pdb $measured >>$n.err 
		$foxs -q $maxq -w $w -e $e mod$n.pdb $measured 2>>$n.err >>$n.out
		nn=`printf '%02d_%.2f_%.3f.dat' $n $w $e`
#		mv mod${n}_pokus1.dat ${n}_${w}_${e}.dat
		mv mod${n}_${measured} $nn
		w=`feval $w + 0.05`
	done
	e=`feval $e + 0.005`
done


cd $SCRATCHDIR
$parsemap -n $n 2>>$n.err

date >>$n.out

# mkdir -p $data/$n
# cp ${n}*.dat $data/$n
cp $n.c12 $n.err $n.out $data

