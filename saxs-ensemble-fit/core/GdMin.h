#ifndef __GDMIN
#define __GDMIN

#include "MinChi.h"
#include "C12Map.h"
#include "Result.h"

class GdMin: public MinChi
{
	long	max_steps;
	long max_min_steps;
	vector<vector<float>> set_w_c_test;
	long set_size;
	vector<float> set_chi2_test;
	const static int MAX_MIN_STEPS =100;

	void generate_random_set();
	void evaluate_set();
	void bobyqa_vector(vector<float> & w_test, float chi2_test, float chi2_best);

protected:
	virtual void step(void);
	virtual bool done(void) { return steps >= max_steps; }
	virtual bool accept(void) { return true; }
	virtual bool polish(void) { return true; }
	virtual void init(void);
	virtual void minimize(int debug);

public:
	GdMin(Curve &me, vector<C12Map> &ma) : MinChi(me, ma) {};
	void setParam(float a)
	{
		alpha = a;
	}

	void setMaxSteps(long s) { max_steps = s; }
	void setSetSize(long s) { set_size = s; }
};

#endif
