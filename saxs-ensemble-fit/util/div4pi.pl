#!/usr/bin/perl

while ($_ = <>) {
	print if /^#/;
	next if /^#/;

	chomp;
	s/^\s+//;
	@F = split /\s+/;

	$F[0] /= 4*3.1415926;
	printf " %13.6E %13.6E %13.6E\n",@F;
}
