#include "MinChi.h"

class BruteForce: public MinChi
{
	bool	really_done;
	float	step_size;
	virtual void init(void);
protected:
	virtual void step(void);
	virtual bool done(void) { return really_done; }
	virtual bool accept(void) { return true; }
public:
	BruteForce(Curve &me, vector<C12Map> &ma) : MinChi(me, ma) {};

	void setStep(float s) { step_size = s; }
	~BruteForce() {}
};
