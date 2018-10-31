#include <limits.h>
#include <math.h>
#include <assert.h>
#include <cstring>
#include <errno.h>

#include <mpi.h>
#include <fstream>
#include <iomanip>
#include <iostream>

#include "Result.h"

float Results::getMinChi2(void)
{
	if (res.size() == 0) return 9.999999e37;
	else return res.begin()->chi2;
}

static bool similar(Result const &r1, Result const &r2)
{
	float	d = 0.;
	int	size = r1.w.size();
	if (size != r2.w.size()) return 0;

	for (int i = 0; i<size; i++) {
		float	dd = r1.w[i] - r2.w[i];
		d +=  dd * dd;
	}

	d = sqrtf(d) / size;

	return d < 0.01;
}

void Results::insert(Result &r)
{
	res.push_front(r);
	res.sort();
	res.unique(similar);
	res.resize(Results::MAX);
}

void Results::synchronize(void)
{
	int	nproc,i;

	MPI_Comm_size(MPI_COMM_WORLD,&nproc);

	int	*mysteps = new int[Results::MAX],
		*allsteps = new int[nproc * Results::MAX];

	i = 0;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++) {
		assert(i < Results::MAX);
		mysteps[i++] = p->step;
	}
	for (; i<Results::MAX; i++) mysteps[i] = 0;

	MPI_Allgather(mysteps,Results::MAX,MPI_INT,
			allsteps,Results::MAX,MPI_INT,
			MPI_COMM_WORLD);

	float	*mychi = new float[Results::MAX],
		*allchi = new float[nproc * Results::MAX];

	i = 0;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++)  {
		if (mysteps[i]) mychi[i] = p->chi2;
		i++;
	}

	MPI_Allgather(mychi,Results::MAX,MPI_FLOAT,
			allchi,Results::MAX,MPI_FLOAT,
			MPI_COMM_WORLD);

	float	*myc = new float[Results::MAX * 3],
		*allc = new float[nproc * Results::MAX * 3];

	i = 0;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++) {
		if (mysteps[i]) {
			myc[3*i] = p->c[0];
			myc[3*i+1] = p->c[1];
			myc[3*i+2] = p->c[2];
		}
		i++;
	}

	MPI_Allgather(myc,Results::MAX * 3,MPI_FLOAT,
			allc,Results::MAX * 3,MPI_FLOAT,
			MPI_COMM_WORLD);

	int	num = res.begin()->w.size();
	float	*myw = new float[Results::MAX * num],
		*allw = new float[nproc * Results::MAX * num];

	i = 0;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++) {
		if (mysteps[i]) 
			for (int j=0; j<num; j++) myw[i*num + j] = p->w[j];
		i++;
	}

	MPI_Allgather(myw,Results::MAX * num,MPI_FLOAT,
			allw,Results::MAX * num,MPI_FLOAT,
			MPI_COMM_WORLD);

	for (i=0; i<nproc * Results::MAX; i++) if (allsteps[i]) {
		Result r;
		r.step = allsteps[i];
		r.chi2 = allchi[i];
		r.c[0] = allc[3*i]; r.c[1] = allc[3*i+1]; r.c[2] = allc[3*i+2];
		r.w.resize(num);
		for (int j=0; j<num; j++) r.w[j] = allw[i*num+j];
		insert(r);
	}

	delete [] mysteps;
	delete [] allsteps;
	delete [] mychi;
	delete [] allchi;
	delete [] myc;
	delete [] allc;
	delete [] myw;
	delete [] allw;
}

int Results::dump(const char *file,int step,int num)
{
	ofstream	f;
	char	tmp[PATH_MAX];
	int	cnt = 0;

	sprintf(tmp,"%s.tmp",file);
	f.open(tmp, ofstream::trunc);
	if (f.fail()) {
		cerr << tmp << ": " << strerror(errno) << endl;
		return 1;	
	}

	f << step << endl;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++) if (p->w.size()) {
		f << setprecision(2) << scientific << p->c[0] << ',' << setprecision(3);
		f << fixed << p->c[1] << ',' << p->c[2] << ',';
	        f << setprecision(6) << sqrtf(p->chi2);
	        f << setprecision(3);
		for (int i = 0; i < p->w.size(); i++)
			f << "," << p->w[i];
		f << endl;
		if (cnt++ == num) break;
	}

	f.close();
	rename(tmp,file);

	return 0; 
}

void Results::print(int rank, int num)
{
	int	cnt = 0;

	cout << "=======" << endl << "rank: " << rank << endl;
	for (list<Result>::iterator p = res.begin(); p != res.end(); p++) if (p->w.size()) {
		cout << "chi: " << sqrtf(p->chi2) <<  endl <<
			"\tc: " << p->c[0] << endl <<
			"\tc1: " << p->c[1] << endl <<
			"\tc2: " << p->c[2] << endl;
		for (int i = 0; i < p->w.size(); i++)
			cout << "\tw[" << i << "]:" << p->w[i] << endl;
		cout << endl;
		if (cnt++ == num) break;
	}
}
