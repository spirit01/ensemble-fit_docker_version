#ifndef __MONTECARLO
#define __MONTECARLO

#include "MinChi.h"

class MonteCarlo: public MinChi
{
	long	max_steps; 
	float	alpha2;

	vector<float>	w_delta;
	float		c_delta[3];

	virtual void init(void);

protected:
	float	beta;

	virtual void step(void);
	virtual bool done(void) { return steps >= max_steps; }
	virtual bool accept(void);

public:
	MonteCarlo(Curve &me, vector<C12Map> &ma) : MinChi(me, ma)
	{
		w_delta.resize(num);
	};
	void setParam(float a, float b)
	{
		alpha = a; beta = b;
		alpha2 = alpha * .5;
	}

	void setMaxSteps(long s) { max_steps = s; }
};

#endif
