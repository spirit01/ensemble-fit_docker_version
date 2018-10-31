#!/usr/bin/perl

$lastchi = 0;
$numfile = 0;
$files = 100;

@G=(0,0,0);

while (($_ = <>) && ($numfile < $files)) {
	@F = split /,/;

	$dist = ($F[0]-$G[0])*($F[0]-$G[0]) + ($F[1]-$G[1])*($F[1]-$G[1]);
	if ($F[2] - $G[2] > 1 || $dist > 0.05) {
		close OUT;
		$fname = sprintf "trace-%03d.dat",$numfile++;
		open OUT,">$fname";
	}
	$,=", ";
#	print OUT $F[0], $F[1], log($F[2]), "\n";
	print OUT $_;
	@G=@F;
}


for $i (0..$files) {
	printf "'trace-%03d.dat' with lines lt palette,",$i;
}
