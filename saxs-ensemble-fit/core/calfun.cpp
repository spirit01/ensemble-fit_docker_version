
#include  "MinChi.h"

extern "C" {

void calfun_(int *n, double *x, double *f)
{
	MinChi	*min = MinChi::getInstance();
	int	nn = *n;

	vector<float> w;
	w.resize(nn);
	for (int i=0; i<nn; i++) w[i] = x[i];

	float chi2 = min->eval(w);
	*f = chi2;
}

} // extern "C"
