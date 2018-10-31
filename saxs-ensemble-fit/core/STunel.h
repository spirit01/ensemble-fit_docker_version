#ifndef __STUNEL
#define __STUNEL

#include "MonteCarlo.h"


class STunel: public MonteCarlo {
	float	gamma;

	float	tunel_cur;

protected:
	virtual bool accept(void);
	virtual void best_callback(void); 
	virtual void synchronize(void);

public:
	STunel(Curve &me, vector<C12Map> &ma) : MonteCarlo(me,ma) { }

	void setParam(float a,float b,float c) {
		MonteCarlo::setParam(a,b);
		gamma = c;
	}
};



#endif
