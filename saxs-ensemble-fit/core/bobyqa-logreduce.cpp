#include <string.h>
#include <math.h>

#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>

extern "C" {
void dsyevr_ (
	char	*jobz,
	char	*range,
	char	*uplo,
	int	*n,
	double	*a,
	int	*lda,
	double	*vl,
	double	*vu,
	int	*il,
	int	*iu,
	double	*abstol,
	int	*m,
	double	*w,
	double	*z,
	int	*ldz,
	int	*isuppz,
	double	*work,
	int	*lwork,
	int	*iwork,
	int	*liwork,
	int	*info
);
}

using namespace std;

template <class F> class Point;

template <class F> class PointBase {
public:
	vector<F>	x;


	template <class G> PointBase<F> & operator =(Point<G> const &);
//	template <class G> PointBase<double> & operator =(PointBase<G> const &);
	template <class G> PointBase<F> & operator +=(PointBase<G> const &);

	PointBase<F>(void) {}; 

	PointBase<F>(int s) {
		x.resize(s); 
		for (int i=0; i<s; i++) x[i] = 0.;
	}

	template <class G> PointBase<F>(PointBase<G> const & g) {
		for (int i=0; i<g.x.size(); i++) x.push_back(g.x[i]);
	}

	PointBase<F> & operator *= (double d) {
		for (int i=0; i<x.size(); i++) x[i] *= d;
	}

	F dotp(vector<F> const &v) const {
		F	ret = 0;

		for (int i=0; i<x.size(); i++) ret += v[i]*x[i];

		return	ret;
	}
};

template <class F> template <class G> PointBase<F> & PointBase<F>::operator=(Point<G> const &f)
{
	x = f.x;

	return *this;
}

template <class F> template <class G> PointBase<F> & PointBase<F>::operator +=(PointBase<G>  const & r)
{
	for (int i=0; i<x.size(); i++) x[i] += r.x[i];
	return *this;
}

template <class F> class Point: public PointBase<F> {
public:
	F	chi2;
	vector<string>	types;

	bool	load(istream &);
};


template <class F> bool Point<F>::load(istream & in)
{
	char	line[BUFSIZ];
	this->x.clear();
	string	s;

#define CLUE	"    Function number"

	while (! in.getline(line,sizeof line).eof() && strlen(line) > 0 && strncmp(line,CLUE,sizeof(CLUE)-1)) ;

	stringstream	parse(line);

//    Function number   284    F =  1.0973091125D+00    
	parse >> s >> s >> s >> s >> s >> chi2;

	while (! in.getline(line,sizeof line).eof() && strlen(line) > 0) {

		F	xx[5] = { FP_NAN, FP_NAN, FP_NAN, FP_NAN, FP_NAN };

		for (int j=0; line[j]; j++) if (line[j] == 'D') line[j] = 'e';
		int n = sscanf(line,"%f %f %f %f %f",xx,xx+1,xx+2,xx+3,xx+4);
		for (int j=0; j<n; j++) this->x.push_back(xx[j]);
	}

	return !in.eof();
}

class Select {
public:
	float	chi2;

	Select() {
		chi2	= 1e38;
	}

	bool match(Point<float> const & p) const {
		if (p.chi2  > chi2) return false;

		return true;
	}
};

#include <boost/program_options.hpp>
namespace po = boost::program_options;

int main(int argc, char ** argv)
{

	po::options_description desc("Options");
	desc.add_options()
		("help", "help message")
		("chi2", po::value<float>()->default_value(100000.0), "select points for dimension reduction - smaller chi2 only")
		("dim", po::value<int>()->default_value(2), "reduce to this number of dimensions")
		("all", "map all points, not only those selected by chi2")
;

	po::variables_map opt;
	try { po::store(po::parse_command_line(argc, argv, desc), opt); }
	catch (exception &e) {
		cerr << argv[0] << ": " << e.what() << endl;
		return 1;
	}
	po::notify(opt);    

	if (opt.count("help")) { cerr << desc; return 1; }

	Select	sel;
	sel.chi2 = opt["chi2"].as<float>();

	int	dimreduce = opt["dim"].as<int>();
	bool allpoints = opt.count("all");

	vector<Point<float> >	pt;
	Point<float>		p;

	while (p.load(cin)) {
		pt.push_back(p);
		if (pt.size() % 100 == 0) cerr << pt.size() << " points read      \r" << flush;
	}
	cerr << pt.size() << " points read      " << endl;


	PointBase<double> sum(pt[0].x.size());
	vector<PointBase<float> > matched;
	long nmatch = 0;

	for (int i=0; i<pt.size(); i++) 
		if (sel.match(pt[i])) {
			PointBase<float>	pb = pt[i];
			matched.push_back(pb);
			sum += pt[i];
			nmatch++;
		}

	cerr << nmatch << " points match criteria" << endl;

	PointBase<float> minusavg(sum);
	double invnmatch = 1. / nmatch;
        minusavg *= - invnmatch;

	for (int i=0; i<matched.size(); i++) matched[i] += minusavg;

	int	npar = pt[0].x.size(), npar2 = npar*npar;
	double *cov = new double[npar2]; // lower triangular
	vector<double>	par(npar);
	
	for (int k=0; k<npar2; k++) cov[k] = 0.;

	for (int n=0; n < nmatch; n++) {
		for (int i=0; i<npar; i++) {
			par[i] = matched[n].x[i];
		}

		for (int i=0; i<npar; i++) {
			int	icol = i*npar;
			for (int j=i; j<npar; j++) cov[icol + j] += par[i] * par[j];
		}
	}

	for (int k=0; k<npar2; k++) cov[k] *= invnmatch;

	double zero = 0., abstol = 0. ;
	int	izero = 0,lwork = npar * 100;
	int	m, *isuppz = new int[2*npar], info, liwork = 10*npar, *iwork = new int[liwork];
	double	*w = new double[npar], *z = new double[npar2], *work = new double[lwork];

	dsyevr_("V", // JOBZ
		"A", // RANGE
		"L", // UPLO
		&npar, // N
		cov, // A
		&npar, // LDA
		&zero, // VL
		&zero, // VU
		&izero, // IL
		&izero, // IU
		&abstol, 
		&m, 
		w,
		z,
		&npar, // LDZ
		isuppz,
		work,
		&lwork,
		iwork,
		&liwork,
		&info);

	cerr << "dsyevr() = " << info << endl;
	if (info) return 1;

	vector<float>	evnorm(npar);
	float	evsum = 0, evcum = 0;

	cerr << "raw eigenvalues: " << endl;
	for (int i=0; i<npar; i++) { cerr << w[i] << " "; evsum += w[i]; }
	cerr << endl;

	cerr << "normalized reverse cummulative: " << endl;
	for (int i=0; i<npar; i++) {
		evnorm[i] = w[npar-i-1] / evsum;
		evcum += evnorm[i];
		cerr << evcum << " ";
	}
	cerr << endl;

	vector<vector<float> > evec(dimreduce);

	for (int i=0; i<dimreduce; i++) {
		evec[i].resize(npar);
		int	icol = (npar-i-1) * npar;
		float	dotp = 0, norm = 0.;
		for (int j=0; j<npar; j++) {
			float	e = evec[i][j] = z[icol+j];
			norm += e*e;
		}
		norm = 1./sqrt(norm)/sqrt(1.*npar);;

		cerr << "eigenvector[" << i << "]:" ;
		for (int j=0; j<npar; j++) {
			cerr << evec[i][j] * norm << " ";
			dotp += evec[i][j] * norm;
		}
		cerr << endl << "dotprod with diagonal: " << dotp << endl;
	}

	for (int i=0; i<pt.size(); i++) 
		if (allpoints || sel.match(pt[i])) {
			for (int j=0; j<dimreduce; j++) {
				cout << pt[i].dotp(evec[j]) << ", ";
			}
			cout << pt[i].chi2;
			cout << endl;
		}


	delete [] isuppz;
	delete [] iwork;
	delete [] w;
	delete [] z;
	delete [] work;

	return 0;
}

