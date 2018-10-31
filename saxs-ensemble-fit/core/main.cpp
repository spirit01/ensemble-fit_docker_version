#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>
#include <strings.h>
#include <sys/types.h>
#include <sys/stat.h>

#include <mpi.h>

#include <iostream>
#include <iomanip>

#include "Curve.h"
#include "C12Map.h"
#include "BruteForce.h"
#include "RandomWalk.h"
#include "MonteCarlo.h"
#include "STunel.h"
#include "GdMin.h"

#define FLOAT_MAX	9.99E37

using namespace std;

static void usage(char const *);

int main(int argc, char ** argv)
{

	const char *prefix = "";
	int	num = -1, syncsteps = 0, bignum = 0;
	long	maxsteps = 5000;
	bool	debug = false, parsed = false, lazy = false;
	enum { BRUTEFORCE, RANDOMWALK, MONTECARLO, STUNEL, GDMIN }	alg = STUNEL;

	char	*fmeasured = 0;
	const char *tprefix = ".";

	MinChi	*min = 0;

	float	alpha = 0.1,beta = 5e-3,gamma = 500;
	long gdmin_set_size = -1;

	MPI_Init(&argc,&argv);

	cout << "# ";
	for (int i=0; i<argc; i++) cout << argv[i] << " ";
	cout << endl;

	int	opt;
	while ((opt = getopt(argc,argv,"n:m:b:da:l:g:s:qy:t:Lp:z:N")) != EOF) switch (opt) {
		case 'n': num = atoi(optarg); break;
		case 'N': bignum = 1; break;
		case 'm': fmeasured = optarg; break;
		case 'l': alpha = atof(optarg); break;
		case 'b': beta = atof(optarg); break;
		case 'g': gamma = atof(optarg); break;
		case 's': maxsteps = atol(optarg); break;
		case 'd': debug = true; break;
		case 'a': if (strcasecmp(optarg,"bruteforce") == 0) alg = BRUTEFORCE;
				  else if (strcasecmp(optarg,"random_walk")==0) alg = RANDOMWALK;
				  else if (strcasecmp(optarg,"montecarlo")==0) alg = MONTECARLO;
				  else if (strcasecmp(optarg,"stunnel")==0) alg = STUNEL;
                  else if (strcasecmp(optarg, "gdmin") == 0) alg = GDMIN;
				  else { usage(argv[0]); return 1; }
			  break;
		case 'q': parsed = true; break;
		case 'y': syncsteps = atoi(optarg); break;
		case 't': tprefix = optarg; break;
		case 'L': lazy = true; break;
		case 'p': prefix = optarg; break;
		case 'z': gdmin_set_size = atol(optarg); break;
		default: usage(argv[0]); return 1;
	}

	if (num<=0 || !fmeasured) { usage(argv[0]); return 1; }
	/* not anymore: assert(num < 100); /* XXX: hardcoded %02d elsewhere */

/* maximal step length (alltogether, not per dimension) */ 
	alpha /= sqrt(2. + num);

/* MC scaling, 5e-3 step up accepted with 10% */
	beta = - log(.1)/beta; 	
	assert(gdmin_set_size<0 || (gdmin_set_size > 0 && alg == GDMIN));

	Curve	measured;

	vector<C12Map>	maps;
	maps.resize(num);

	if (measured.load(fmeasured)) return 1;

	for (int i=0; i<num; i++) {
		char	buf[PATH_MAX];

/* used to align generated curves */		
		maps[i].setMeasured(measured);

		if (lazy) {
			if (num < 100 && !bignum)
				snprintf(buf,sizeof buf,"%s%02d.pdb",prefix,i+1);
			else 
				snprintf(buf,sizeof buf,"%s%02d/%04d.pdb",prefix,(i+1)/100,i+1);

			maps[i].setQMax(measured.getQMax());
			maps[i].setSize(measured.getSize());
			if (maps[i].setLazy(buf,fmeasured)) return 1;
		}
		else if (parsed) {
			snprintf(buf, sizeof buf, "%s%02d.c12",prefix,i+1);
			if (maps[i].restore(buf)) return 1;
			maps[i].alignScale(measured);
		}
		else {
			snprintf(buf,sizeof buf,"%s%02d/%02d_%%.2f_%%.3f.dat",prefix,i+1,i+1);
			if (maps[i].load(buf)) return 1;
			maps[i].alignScale(measured);
		}
	}

	switch (alg) {
		case BRUTEFORCE: {
			BruteForce *b =	new BruteForce(measured,maps);
			b->setStep(.01);
			min = b;
			break;
		}
		case RANDOMWALK: {
			RandomWalk *r = new RandomWalk(measured,maps);
			r->setParam(alpha);
			r->setMaxSteps(maxsteps);
			min = r;
			break;
		}
		case MONTECARLO: {
			MonteCarlo *m = new MonteCarlo(measured,maps);
			m->setParam(alpha,beta);
			m->setMaxSteps(maxsteps);
			min = m;
			break;
		}
		case STUNEL: {
			STunel *t = new STunel(measured,maps);
			t->setParam(alpha,beta,gamma);
			t->setMaxSteps(maxsteps);
			min = t;
			break;
		}
		case GDMIN: {
			GdMin *g = new GdMin(measured, maps);
			g->setParam(alpha);
			g->setMaxSteps(maxsteps);
			g->setSetSize(gdmin_set_size);
			min = g;
			break;
		}
		default:
			cerr << "algorithm " << alg << " not implemented" << endl;
			return 1;
	}

	min->setSyncSteps(syncsteps);


	int	rank;

	MPI_Comm_rank(MPI_COMM_WORLD,&rank);

	if (debug) {
		char	buf[PATH_MAX];

		mkdir(tprefix,0755);
		snprintf(buf,PATH_MAX,"%s/ensamble-fit_%d.trc",tprefix,rank);
		if (min->openTrace(buf) == NULL) return 1;
	}

	min->minimize(debug);

	MPI_Finalize();

}

static void usage(char const *me)
{
	cerr << "usage: mpirun <options> " << me <<  " <options>" << endl <<
		"	-n num 		number of models (mandatory)" << endl << 
		"	-m measured	experimental data (mandatory)" << endl <<
		"	-l alpha	max step length (default 0.1)" << endl <<
		" 	-b beta		scaled Metropolis factor, accept this increase with 10% (default 0.005)" << endl <<
		"	-g gamma	exponential factor in stochastic tunnelling (default 500)" << endl <<
		"	-s steps	major optimization steps" << endl <<
		"	-d 		debug" << endl <<
		"	-a 		algorithm, one of bruteforce/random_walk/gdmin/montecarlo/stunnel (default stunnel)" << endl <<
		"	-q		use pre-parsed maps of c1-c2 (output of parse-map)" << endl <<
		"	-y syncsteps	steps between inter-processes synchronization (default 0 -- don't sync)" << endl <<
		"	-t trace	prefix for trace files" << endl <<
		"	-L		be lazy, compute single SAXS curves on the fly, not all in advance" << endl <<
		"	-p prefix	model file prefix" << endl;
}
