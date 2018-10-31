#ifndef __C12Map
#define __C12Map

#include <vector>
#include "Curve.h"

namespace IMP {
    namespace saxs {
        class Profile;        
    }
}

class C12Map
{
	float	c1min,c1max;
	float	c2min,c2max;
	int	c1samples, c2samples;
	float	c1step,c2step;
	float	qmax;
	int	size;

	std::vector<std::vector<Curve> >	curves;

	bool	is_lazy;
	char const	*lazy_pdb,*lazy_profile;
	class	IMP::saxs::Profile	*imp_profile;

	void lazyCurve(int ic1,int ic2);

	static char const *FOXS;

	Curve const * measured;

public:
	C12Map();

	int setLazy(char const *pdb,char const *dat);

	void setRange(float min1,float max1,int samples1,
		float min2, float max2, int samples2);
	void setQMax(float q) { qmax = q; }
	void setSize(int s) { size = s; }
	int load(char const *tmpl);
	void interpolate(float c1, float c2, Curve& out);

	void alignScale(Curve const &ref);

	int dump(char const *fname);
	int restore(char const *fname);

	float trueC1(float c1) const { return c1min + c1 * (c1max-c1min); }
	float trueC2(float c2) const { return c2min + c2 * (c2max-c2min); }

	void setMeasured(const Curve & m) { measured = &m; }
};

#endif
