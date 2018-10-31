#ifndef __RANDOMWALK
#define __RANDOMWALK

#include "MinChi.h"

class RandomWalk: public MinChi
{
	long	max_steps; 

	virtual void init(void);

protected:
	virtual void step(void);
	virtual bool done(void) { return steps >= max_steps; }
	virtual bool accept(void) { return true; }
	virtual bool polish(void) { return true; }

public:
	RandomWalk(Curve &me, vector<C12Map> &ma) : MinChi(me, ma) {};
	void setParam(float a)
	{
		alpha = a;
	}

	void setMaxSteps(long s) { max_steps = s; }
};

#endif
