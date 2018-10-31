#!/usr/bin/perl

while ($_ = <>) {
	print if /^#/;
	next if /^#/;

	chomp;
	s/^\s+//;
	@F = split /\s+/;

	$F[0] /= 10;
	printf " %13.6E %13.6E %13.6E\n",@F;
}
