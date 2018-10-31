#include <stdlib.h>
#include <math.h>
#include <cstring>
#include <mpi.h>

#include "GdMin.h"
#include "bobyqa.h"

void GdMin::minimize(int debug)
{
	interpolated.resize(num);
	bool	got_best = false;
	long index_selected_vector = -1;

	merged.assign(measured.getQ(),measured.getI());
	w_test.resize(num+2);

	init();


	int	rank;
	MPI_Comm_rank(MPI_COMM_WORLD,&rank);

	/* evaluate whole set */
	evaluate_set();

	while (!done()) {
		/* choose next w_test from set */
		step();
		steps++;

		int	type = 'R';
		/* minimize with bobyqa */
		if (polish()) {
			float chi2_best;
			chi2_test = eval(w_test);
			if (!got_best) {
				got_best = true;
				chi2_best = 1.01 * chi2_test;
			}
			else {
				chi2_best = results.getMinChi2();
			}

			/* polish the minimum with local optimization */
			bobyqa_vector(w_test, chi2_test, chi2_best);

			normalize(w_test,num);

			/* evaluate minimized vector */
			Result	p;
			p.chi2 = eval(w_test);
			p.c[0] = c_test[0]; // XXX: sideeffect in eval()
			p.c[1] = maps[0].trueC1(w_test[num]);
			p.c[2] = maps[0].trueC2(w_test[num+1]);
			p.w = w_test;
			p.w.resize(num);
			p.step = steps;
			/* if the minimized vector is good enough, insert to results and remove the original from set (to avoid repeated selection) */
			if (accept()) {
				results.insert(p);
				w_cur = w_test;
				for (int i=0; i<3; i++) { c_cur[i] = c_test[i]; }
				chi2_cur = chi2_test;
				best_callback();
				type = 'B';
			}
			else type = 'A';

		}

		if (syncsteps && steps % syncsteps == 0) {
			float	oldchi2 = results.getMinChi2();
			synchronize();
			if (oldchi2 > results.getMinChi2()) best_callback();

			if (rank == 0) results.dump("results",steps,10);
		}

		if (debug) writeTrace(type);
	}
	synchronize();
	if (rank == 0) {
		results.dump("result",steps);
		results.print(rank);
	}
}

void GdMin::generate_random_set()
{
	set_w_c_test.resize(set_size);
	for (long j=0; j<set_size; j++) {

		set_w_c_test[j].resize(num+2);
		float	sum = 0.;
		for (int i=0; i<num; i++) sum += (set_w_c_test[j][i] = drand48());


		float rsum = 1./sum;
		for (int i=0; i<num; i++) set_w_c_test[j][i] *= rsum;

		for (int i=1; i<3; i++) {
			set_w_c_test[j][num+i-1] = drand48();
		}
	}
}

void GdMin::evaluate_set()
{
	for (long i=0; i<set_size; i++){
		set_chi2_test[i] = eval(set_w_c_test[i]);
	}
}

void GdMin::bobyqa_vector(vector<float> & w_test, float chi2_test, float chi2_best)
{
	double	x[num+2];
	double xu[num+2],xl[num+2];
	for (int i=0; i<num+2; i++) {
		xl[i] = 0.;
		xu[i] = 0.99999;
	}

	int	n = num+2, npt = 2*n+1, iprint = /* 2 */ 0, maxfun = GdMin::MAX_MIN_STEPS;
	double 	rbeg = alpha;
	double rend = alpha/100;/*fabs(chi2_test-chi2_best)/1000.;*/ /* XXX: may not work well with randomwalk */

	double	w[(npt+5)*(npt+n)+3*n*(n+5)/2];

	for (int i=0; i<num+2; i++) x[i] = w_test[i];
	bobyqa_(&n,&npt,x,xl,xu,&rbeg,&rend, &iprint,&maxfun,w);
	for (int i=0; i<num+2; i++) w_test[i] = x[i];

}

void GdMin::init()
{
	//generate set
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

	generate_random_set();
	w_cur = set_w_c_test[0];
	for (int i=1; i<3; i++) c_cur[i] = set_w_c_test[0][num+i-1];

	set_chi2_test.resize(set_size);
	for (long i=0; i<set_size; i++)
		set_chi2_test[i] = 0;
	steps = 0;
}

void GdMin::step()
{
	/* find the best chi2 from set_chi2_test */
	float min = 9.999999e37;
	long index = -1;
	for (long i=0; i<set_size; i++) {
		if (set_chi2_test[i] < min && set_chi2_test[i] >= 0){
			min = set_chi2_test[i];
			index = i;
		}
	}

	/* we mark the selected chi2 -1 to avoid repeated selection */
	set_chi2_test[index] = -1;

	w_test = set_w_c_test[index];
}
