#include <stdlib.h>
#include <math.h>
#include <cstring>
#include <mpi.h>

#include "MonteCarlo.h"

void MonteCarlo::step()
{
/* generate delta */
	for (int i=0; i<num; i++) {
		do {
			w_delta[i] = drand48();
			w_delta[i] = alpha * w_delta[i] - alpha2;
			w_test[i] = w_cur[i] + w_delta[i];
		} while (w_test[i] < 0. || w_test[i] > 1.);
	}

	for (int i=1; i<3; i++) {
		do {
			c_delta[i] = drand48();
			c_delta[i] = alpha * c_delta[i] - alpha2;
			c_test[i] = c_cur[i] + c_delta[i];
		} while (c_test[i] < 0. || c_test[i] > 1.);
	}
}

bool MonteCarlo::accept()
{
	float	pen = c12penalty(),
		p = expf(-beta * (chi2_test+pen - chi2_cur)),
		r = drand48();

	return r < p || steps == 1;
}

void MonteCarlo::init()
{
	int	rank;
	union	{
		char	s[16];
		long	l;
	} u;

	strcpy(u.s,"M@g#cN*mb&R");
	srand48(u.l);

	MPI_Comm_rank(MPI_COMM_WORLD, &rank);

	for (int i=0; i<num*rank; i++) drand48();

	float	sum = 0.;

	for (int i=0; i<num; i++) sum += (w_cur[i] = drand48());
	for (int i=0; i<num; i++) w_cur[i] /= sum;

	c_cur[1] = drand48()*.8 + .1;
	c_cur[2] = drand48()*.8 + .1;
	steps = 0;
}

