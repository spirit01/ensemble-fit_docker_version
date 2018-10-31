#include "BruteForce.h"

void BruteForce::step()
{
	int	i = 0;

	c_test[1] = c_cur[1];
	c_test[2] = c_cur[2];

	w_test = w_cur;

	if ((c_test[1] += step_size) >= 1.) {
		c_test[1] = 0.;
		if ((c_test[2] += step_size) >= 1.) {
			c_test[2] = 0.;
			for (i=0; i<num; i++) if ((w_test[i] += step_size) >= 1.) {
				w_test[i] = 0.; 
				continue;
			} else break;
		}
	}
	
	if (i == num) really_done = true;
}

void BruteForce::init()
{
	for (int i=0; i<num; i++) w_cur[i] = 0;
	c_cur[1] = c_cur[2] = 0;
	really_done = false;
}

