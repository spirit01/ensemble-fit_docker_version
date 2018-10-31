#include <stdlib.h>
#include <math.h>
#include <cstring>
#include <mpi.h>

#include "RandomWalk.h"

void RandomWalk::step()
{
/* generate delta */
	float	sum = 0.;

	for (int i=0; i<num; i++) sum += (w_test[i] = drand48());

	float rsum = 1./sum;
	for (int i=0; i<num; i++) w_test[i] *= rsum;

	for (int i=1; i<3; i++) {
		c_test[i] = drand48();
	}
}

void RandomWalk::init()
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

	step();
	w_cur = w_test;
	for (int i=1; i<3; i++) c_cur[i] = c_test[i];

	steps = 0;
}

