#include <iostream>

#include <assert.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "Curve.h"
#include "C12Map.h"

using namespace std;

/* usage: measured.dat num_map */
bool fit = false;

/* usage: c2 num_map */
bool curve = true;


int main(int argc, char **argv)
{
	C12Map	map;
	char	buf[PATH_MAX];

	float	c1range[] = { .95, 1.05 },
		c2range[] = { -2., 4. };

	int	c1steps = 6, c2steps = 13;

	map.setRange(c1range[0],c1range[1],c1steps,
			c2range[0],c2range[1],c2steps);

	assert(argc >= 3);
	snprintf(buf,sizeof buf,"%s/%s_%%.2f_%%.3f.dat",argv[2],argv[2]);
	map.load(buf);

	Curve	interpolated;
	Curve	measured;

	if (fit) measured.load(argv[1]);

	c1steps = 100;
	c2steps = 45;

	float	c2;

	if (curve) c2 = atof(argv[1]);

	for (int i=0; i<c1steps; i++) {
		float	c1 = c1range[0] + i*(c1range[1] - c1range[0])/c1steps;

		if (fit) for (int j=0; j<c2steps; j++) {
			float	c2 = c2range[0] + j*(c2range[1] - c2range[0])/c2steps;

			map.interpolate(c1,c2,interpolated);

			float	chi2, c;
			interpolated.fit(measured,chi2,c);
			cout << c1 << " " << c2 << " " << sqrt(chi2) << endl;
		}
		else if (curve) {

			map.interpolate(c1,c2,interpolated);

			vector<float> const & I = interpolated.getI(),
				& q = interpolated.getQ();

			for (int j=0; j<q.size(); j++) 
				cout << c1 << " " << q[j] << " " << I[j]  << endl;
		}
	}
			

}
