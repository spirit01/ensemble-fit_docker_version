#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>

#include <iostream>

#include "Curve.h"
#include "C12Map.h"

#define FLOAT_MAX	9.99E37

// Just test, disable tunelling
#define PURE_MONTE_CARLO

using namespace std;

static void usage(char const *);

int main(int argc, char ** argv)
{

	char	prefix[PATH_MAX] = "";
	int	num = -1, startwith = 0;
	int	maxsteps = 5000;
	bool	debug = false;

	char	*fmeasured;

	float	alpha = 0.05,beta = 5e-3 ,gamma = 1;

	int	opt;
	while ((opt = getopt(argc,argv,"n:m:b:d")) != EOF) switch (opt) {
		case 'n': num = atoi(optarg); break;
		case 'm': fmeasured = optarg; break;
		case 'b': beta = atof(optarg); break;
		case 'd': debug = true; break;
		default: usage(argv[0]); return 1;
	}

	if (num<=0) { usage(argv[0]); return 1; }


/* maximal step length (alltogether, not per dimension) */ 
	alpha = powf(alpha,1./num);

/* MC scaling, 5e-3 step up accepted with 10% */
	beta = - log(.1)/beta; 	

/* tunnel scaling */
//	gamma = 1;

/* XXX: works fine with defaults, options/config later */

	float	c1range[] = { .95, 1.05 },
		c2range[] = { -2., 4. };
/* real reasonable values */
 	int	c1steps = 21, c2steps = 121;

/* FIXME: just test */
	c1steps = 5; c2steps = 13;



/* 0 .. num-1 -- weights of conformations 
   num, num+1 -- normalized c1, c2
*/

	vector<float>	cur,delta,test,best;
	cur.resize(num+2);
	delta.resize(num+2);
	test.resize(num+2);
	best.resize(num+2);

	float	chi2, chi2min = FLOAT_MAX,
		curtunel = 0;

	Curve	merged,measured;
	vector<Curve>	interpolated;
	interpolated.resize(num);

	vector<C12Map>	maps;
	maps.resize(num);

	for (int i=0; i<num; i++) {
		char	buf[PATH_MAX];

		snprintf(buf,sizeof buf,"%s%02d/%02d_%%.2f_%%.3f.dat",prefix,i+1,i+1);
		maps[i].setRange(c1range[0],c1range[1],c1steps,
				c2range[0],c2range[1],c2steps);
		if (maps[i].load(buf)) return 1;
	}

	if (measured.load(fmeasured)) return 1;
	
	merged.assign(measured.getQ(),measured.getI());

	for (int i=0; i<num; i++) cur[i] = 0.;
	cur[startwith] = 1.;

	cur[num] = cur[num+1] = .5;

	float alpha2 = alpha * .5;
	float	c,c1,c2;

	for (int step=0; step < maxsteps; step++) {


/* generate delta */
		for (int i=0; i<=num+1; i++) {
			do {
				delta[i] = drand48();
				delta[i] = alpha * delta[i] - alpha2;
				test[i] = cur[i] + delta[i];
			} while (test[i] < 0. || test[i] > 1.);
		}

/* denormalize c1,c2 */
		c1 = c1range[0] + test[num] * (c1range[1] - c1range[0]);
		c2 = c2range[0] + test[num+1] * (c2range[1] - c2range[0]);

/* normalize weights (not strictly necessary but ...) */
		float w = 0;
		for (int i=0; i<num; i++) w += test[i];
		w = 1./w;
		for (int i=0; i<num; i++) test[i] *= w;

		for (int i=0; i<num; i++) maps[i].interpolate(c1,c2,interpolated[i]);

		merged.mergeFrom(interpolated,test);
		merged.fit(measured, chi2, c);

		float tunel = 1 - exp(-gamma * (chi2 - chi2min));

#ifdef PURE_MONTE_CARLO
		tunel = chi2;
#endif

		float	p = exp(-beta * (tunel - curtunel));

		if (debug) {
			for (int i=0; i<num; i++) cout << test[i] << " ";
			cout << c1 << " " << c2 << " ";
		}
		if (drand48() < p || step==0) {
			/* accept */
			cur = test;
			curtunel = tunel;
			if (chi2 < chi2min) {
				chi2min = chi2;
				best = cur;
#ifndef PURE_MONTE_CARLO
				curtunel = 0;		// XXX: ??
#endif 
			}
			if (debug) cout << "A\tchi2=" << chi2 << "\tchi=" << sqrt(chi2) << "\tc=" << c << endl;
		}
		else if (debug) cout << "R" << endl;
	}

	cout << "best: ";
	for (int i=0; i<num; i++) cout << test[i] << " ";
	cout << c1 << " " << c2;
	cout << "\tchi2=" << chi2 << "\tchi=" << sqrt(chi2) << "\tc=" << c << endl;

}

static void usage(char const *me)
{
	cerr << "usage: " << me << " -n num -m measured " << endl;
}
