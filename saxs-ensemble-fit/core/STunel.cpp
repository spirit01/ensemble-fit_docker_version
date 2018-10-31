#include <math.h>
#include <stdlib.h>
#include <mpi.h>

#include "STunel.h"

bool STunel::accept()
{
	float	pen = c12penalty(),
		tunel = 1 - expf(-gamma * (chi2_test+pen - results.getMinChi2()));

	float	p = expf(-beta * (tunel - tunel_cur)),
		r = drand48();

	if (r < p || steps == 1) {
		tunel_cur = tunel;
		return true;
	}
	return false;
}

void STunel::synchronize()
{
	struct	{
		float	chi2;
		int	idx;
	} snd,rec;
	
	MinChi::synchronize();

/*
	if (step_best > 0)  MPI_Comm_rank(MPI_COMM_WORLD,&snd.idx);
	else snd.idx = -step_best;

	snd.chi2 = chi2_best;

	MPI_Allreduce(&snd,&rec,1,MPI_FLOAT_INT,MPI_MINLOC,MPI_COMM_WORLD);

	chi2_best = rec.chi2;
	best_callback();

	if (rec.idx != snd.idx) step_best = -rec.idx;
*/
}

void STunel::best_callback() 
{
	tunel_cur = 1 - expf(-gamma * (chi2_cur - results.getMinChi2()));
}
