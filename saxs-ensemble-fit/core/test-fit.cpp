#include <iostream>

#include "Curve.h"

using namespace std;

int main(int argc, char **argv)
{
	Curve	c1,c2;

	float	c,chi2;

	if (c1.load(argv[1]) || c2.load(argv[2],false)) return 1;

	c2.fit(c1,chi2,c);

	cout << chi2 << " " << c << endl;
	
	return 0;
}
