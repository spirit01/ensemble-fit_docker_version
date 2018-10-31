#!/usr/bin/perl

use Getopt::Std;

getopt('x');

if ($opt_x) {
	($x_min,$x_max) = split /-/,$opt_x;
}

while ($_ = <>) {
	chomp;
	if (/^MODEL\s+([[:digit:]]+)/) {
		close F;
		$n = sprintf "%02d",$1;
		open F,">mod$n.pdb";
	}
	elsif ($opt_x) {
		@F = split;
		print F $_,"\n" if $F[5] < $x_min || $F[5] > $x_max;
	}
	else {
		print F $_,"\n";
	}
}
