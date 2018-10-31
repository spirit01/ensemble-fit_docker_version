#include <fstream>
#include <iostream>
#include <sstream>
#include <assert.h>
#include <stdlib.h>
#include <math.h>

#include "Curve.h"


using namespace std;

Curve::Curve()
{
	qmin = qmax = step = 0;
	has_data = false;
}

#if 0
void Curve::setScale(float min,float max, int s)
{

	abort();

	qmin = min;
	qmax = max;
	steps = s;

	float	qstep = (qmax-qmin)/steps;

	assert(steps>0);

	I.resize(steps);
	err.resize(steps);

/* XXX: poor man, casem rozumnou interpolaci */

	vector<float>::iterator i = rawQ.begin(), b = i; 
	float q = qmin;
	int	idx = 0;

	assert(*i <= qmin);

	while (i != rawQ.end() && q < qmax) {
		if (*i < q) {
			while (i != rawQ.end() && *i < q) i++;
			I[idx] = rawI[i-b];
			err[idx] = rawErr[i-b]; 
			idx++;
			q += qstep;
		}
		else {
			while (q < qmax && q < *i) {
				I[idx] = rawI[i-b];
				err[idx] = rawErr[i-b]; 
				idx++;
				q += qstep;
			}
		}

	}
}
#endif

void Curve::assign(vector<float> const &q, vector<float> const & I)
{
	rawQ = q;
	rawI = I;
	rawErr.clear();
	has_error = false;
	has_data = true;
}

void Curve::assign(vector<float> const &q, vector<float> const & I, vector<float> const &err)
{
	assign(q,I);
	rawErr = err;
	has_error = true;
	has_data = true;

	scaleFromRaw();

}

void Curve::scaleFromRaw()
{
	int	steps = rawQ.size();

	qmin = rawQ[0];
	qmax = rawQ[steps-1];
	qmax += (qmax - qmin)/(steps-1);

//	this->I = rawI; this->err = rawErr;

}


int Curve::load(char const *file,bool dat)
{
	char	line[BUFSIZ];
	ifstream	in;

	rawQ.clear();
	rawI.clear();
	rawErr.clear();

	in.open(file);
	if (in.fail()) {
		cerr << "open: " << file << endl;
		return 1;
	}

// cerr << "load " << file << endl;
	while (! in.getline(line,sizeof line).eof()) {
		istringstream parse(line);

		if (line[0] != '#') {
			float	q,i,e;
			parse >> q >> i >> e;

			rawQ.push_back(q);
			if (dat) {
				rawI.push_back(i);
				rawErr.push_back(e);
			}
			else rawI.push_back(e);
// cerr << q << " " << i << " " << e << endl;
		}
	}
	in.close();
	scaleFromRaw();
	has_error = dat;
	has_data = true;
	return 0;
} 

int Curve::checkScale(Curve const &ref) const
{
	const float tol = 1e-8;

	return fabs(qmin - ref.qmin) < tol &&
		fabs(qmax - ref.qmax) < tol &&
		fabs(step - ref.step) < tol;
}


void Curve::mergeFrom(vector<Curve> const & curves,vector<float> const & weights)
{
	int 	ncurves = curves.size();
	int	steps = rawQ.size();

	assert(checkScale(curves[0]));
	assert(ncurves <= weights.size());
	assert(curves[0].rawQ.size() == steps);

	for (int i=0; i<steps; i++) rawI[i] = 0;

	for (int j=0; j<ncurves; j++) {
		vector<float> const & jI = curves[j].getI();
		float	jw = weights[j];
		for (int i=0; i<steps; i++) rawI[i] += jI[i] * jw;
	}
	has_data = true;
}

void Curve::fit(Curve const &measured, float &chi2, float &c) const
{
	vector<float> const & Ie = measured.getI(),
		& I = getI(),
		& sigma = measured.getErr();

	assert(measured.hasErr());

	int	size = I.size();
	assert(Ie.size() == size);

	double a = 0, b = 0;

	for (int i=0; i<size; i++) {
		float sigma2 = sigma[i] * sigma[i];
		sigma2 = .5/sigma2;

		a += I[i]*I[i]*sigma2;
		b += I[i]*Ie[i]*sigma2;
	}

	c = b/a;
	
	double out = 0;

//	cerr << "fit...... " << endl;
	for (int i=0; i<size; i++) {
		float sigma2 = sigma[i] * sigma[i];

		float	x = Ie[i] - c*I[i];
		x *= x;

		out += x/sigma2;
//		cerr << x << " " << out << endl;
	}
	chi2 = out/size;
}

void Curve::alignScale(Curve const &ref)
{
	assert(!has_error);

	int	newSize = ref.getSize(), size=getSize();
	vector<float>	newI(newSize);
	vector<float> const & refQ = ref.getQ();

	int	iq = 0;
	for (int i=0; i<newSize; i++) {
		float	q = refQ[i];
		for (; iq<size && rawQ[iq]<q; iq++);	
		if (iq == 0) {
			float 	k = (rawI[1]-rawI[0])/(rawQ[1]-rawQ[0]);
			newI[i] = rawI[0] - k * (rawQ[0] - q);
		}
		else if (iq == size) {
			float 	k = (rawI[size-1]-rawI[size-2])/(rawQ[size-1]-rawQ[size-2]);
			newI[i] = rawI[size-1] + k * (q-rawQ[size-1]);
		}
		else {
			float	w = (q - rawQ[iq-1]) / (rawQ[iq] - rawQ[iq-1]);
			newI[i] = (1.-w) * rawI[iq-1] + w * rawI[iq];
		}
	}

	rawQ = ref.getQ();
	rawI = newI;

	scaleFromRaw();
}
