#ifndef __CURVE_H
#define __CURVE_H

#include <vector>

using namespace std;

class Curve
{
	vector<float>	rawQ, rawI, rawErr;
	bool	has_error, has_data;

	float	qmin, qmax, step;
//	float	*q;
//
	
	void	scaleFromRaw(void);

public:
	Curve();

	void reset(int size,bool err) {
		rawQ.resize(size); 
		rawI.resize(size); 
		rawErr.resize((has_error = err) ? size : 0); 
	}

	int	load(char const *file,bool dat = true);
	void	assign(vector<float> const &q, vector<float> const & I, vector<float> const &err);
	void	assign(vector<float> const &q, vector<float> const & I);

	int	checkScale(Curve const &ref) const;
	void	alignScale(Curve const & ref);

	void	mergeFrom(vector<Curve> const &curves,vector<float> const & weights);

	void 	fit(Curve const &measured, float &chi2, float &c) const;

/* XXX: no interpolation for the time being */
	vector<float> const & getQ(void) const { return rawQ; }
	vector<float> const & getI(void) const { return rawI; }
	vector<float> const & getErr(void) const { return rawErr; }

	bool hasErr(void) const { return has_error; }
	bool hasData(void) const { return has_data; }
	int getSize(void) const { return rawQ.size(); }

	float getQMax(void) const { return qmax; }
};

#endif
