#!/usr/bin/perl

while ($_ = <>) {
	print if /^#/;
	next if /^#/;

	chomp;
	s/^\s+//;
	@F = split /\s+/;

	next if $F[1] < 0;
	print $_,"\n";
}
