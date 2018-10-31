#ifndef __MINCHI
#define __MINCHI

#include <stdio.h>
#include <assert.h>

#include "C12Map.h"
#include "Result.h"

class MinChi
{
	static MinChi	*inst;

	virtual bool accept(void) = 0;
	virtual void step(void) = 0;
	virtual void init(void) = 0;
	virtual bool done(void) = 0;

	virtual bool polish(void) { return chi2_test < results.getMinChi2(); }

	const static int MAX_MIN_STEPS = 1000;


protected:
	vector<Curve>   interpolated;
	Curve		merged;
	int	num;
	long	steps;
	long	syncsteps;

	float	alpha;
	float	chi2_cur, chi2_test ;
	Results	results;

	FILE	*trace;

	vector<float>	w_cur, w_test;

	float	c_cur[3],c_test[3];

	vector<C12Map>	&maps;
	Curve 		&measured;

	virtual void best_callback(void) {}
	virtual float c12penalty(void);
	virtual void synchronize(void) { results.synchronize(); }
	

public:
	MinChi( Curve &me, vector<C12Map> &ma): 
		measured(me), maps(ma)
		{
			assert(MinChi::inst == 0);
			MinChi::inst = this;
			syncsteps = 0;
			num = ma.size();
			w_cur.resize(num);
			w_test.resize(num);
			trace = NULL;
		}

	static MinChi *getInstance(void) { return MinChi::inst; }
	static void normalize(vector<float> & ww, int num);

	void setMaps(vector<C12Map> &m) { maps = m; }
	void setMeasured(Curve &c) { measured = c; }
	void setSyncSteps(long s) { syncsteps = s; }

/*
	vector<float> & getBestW(void) { return w_best; }
	float const * getBestC(void) { return c_best; }
	float getBestChi2(void) { return chi2_best; }
	long getBestStep(void) { return step_best; }
*/

	virtual void minimize(int debug);

	FILE* openTrace(const char *);
	void writeTrace(int);

	float eval(vector<float> const &wc);
};

#endif
