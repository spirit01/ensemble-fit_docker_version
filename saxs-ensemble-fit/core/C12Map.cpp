#include <stdio.h>
#include <stdlib.h>
#include <limits.h>
#include <assert.h>
#include <errno.h>
#include <string.h>
#include <unistd.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <sys/wait.h>

#include <fcntl.h>

#include <iostream>
#include <fstream>

#include <IMP/saxs/Profile.h>
#include <IMP/saxs/utility.h>

#include "C12Map.h"

// #define DEBUG_IPOL

char const *C12Map::FOXS;

C12Map::C12Map()
{
/* XXX: works fine with defaults, options/config later */

	float	c1range[] = { .95, 1.05 },
		c2range[] = { -2., 4. };
/* real reasonable values */
 	int	c1steps = 21, c2steps = 121;

/* FIXME: just test */
//	c1steps = 5; c2steps = 13;
//
	setRange(c1range[0],c1range[1],c1steps,
		c2range[0],c2range[1],c2steps);
	is_lazy = false;
	qmax = 0.5;

	FOXS = "foxs";
}

int C12Map::setLazy(char const *p,char const *d)
{
	ifstream	in;
/*
	in.open(p);
	if (in.fail()) {
		cerr << "open: " << p << endl;
		return 1;
	}
	in.close();
*/
	std::vector<IMP::Particles>	pv;
	std::vector<std::string>	fnames;

	IMP_NEW(IMP::Model, m, ());
	IMP::saxs::read_pdb(m,p,fnames,pv);

	double	dstep = double(qmax)/size;

	imp_profile = new IMP::saxs::Profile(0,dstep*(size-1),dstep);	/* XXX: qmax is also "+1" */
	imp_profile->calculate_profile_partial(pv[0]);
	
	in.open(d);
	if (in.fail()) {
		cerr << "open: " << d << endl;
		return 1;
	}
	in.close();

	is_lazy = true;
	lazy_pdb = p;
	lazy_profile = d;

	curves.resize(c1samples);
	for (int ic1 = 0; ic1 < c1samples; ic1++)
		curves[ic1].resize(c2samples);

	return 0;
}

void C12Map::setRange(float min1,float max1,int samples1,
	float min2, float max2, int samples2)
{
	c1min = min1; c2min = min2;
	c1max = max1; c2max = max2;
	c1samples = samples1; c2samples = samples2;

	c1step = (c1max-c1min)/(c1samples-1);
	c2step = (c2max-c2min)/(c2samples-1);

}

int C12Map::load(char const *tmpl)
{
	curves.resize(c1samples);
	for (int ic1 = 0; ic1 < c1samples; ic1++) {
		curves[ic1].resize(c2samples);
		float c1 = c1min + c1step * ic1;
		for (int ic2 = 0; ic2 < c2samples; ic2++) {
			float c2 = c2min + c2step * ic2;

			char	buf[PATH_MAX];
			snprintf(buf,sizeof buf,tmpl,c2,c1);

			if (curves[ic1][ic2].load(buf,false)) return 1;
		}
	}

	return 0;
}

void C12Map::interpolate(float c1, float c2, Curve& out)
{
	int	ic1 = (c1-c1min)/c1step,
		ic2 = (c2-c2min)/c2step;

	float 	wc1 = c1 - c1min - ic1*c1step,
		wc2 = c2 - c2min - ic2*c2step;

	assert(ic1>=0); assert(ic2>=0);
	assert(ic1<c1samples-1); assert(ic2<c2samples-1);

	wc1 /= c1step;
	wc2 /= c2step;

	float	w[2][2] = {
		{ (1.F-wc1)*(1.F-wc2), (1.F-wc1)*wc2 },
		{ wc1*(1.F-wc2), wc1*wc2 }
	};

	if (is_lazy) {
		if (! curves[ic1][ic2].hasData()) lazyCurve(ic1,ic2);
		if (! curves[ic1+1][ic2].hasData()) lazyCurve(ic1+1,ic2);
		if (! curves[ic1][ic2+1].hasData()) lazyCurve(ic1,ic2+1);
		if (! curves[ic1+1][ic2+1].hasData()) lazyCurve(ic1+1,ic2+1);
	}

	vector<float> const * oldI[2][2] = {
		{ &curves[ic1][ic2].getI(), &curves[ic1][ic2+1].getI() },
		{ &curves[ic1+1][ic2].getI(), &curves[ic1+1][ic2+1].getI() }
	};

	vector<float>	newI;

	int size = curves[ic1][ic2].getSize();
	newI.resize(size);

	for (int i=0; i<size; i++) {
		newI[i] = w[0][0] * (*oldI[0][0])[i] +
			w[0][1] * (*oldI[0][1])[i] +
			w[1][0] * (*oldI[1][0])[i] +
			w[1][1] * (*oldI[1][1])[i];
	}

#ifdef DEBUG_IPOL
	std::cerr << c1 << " " << c2 << " " << 
		ic1 << " " << ic2 << " " <<
		w[0][0] << " " << 
		w[0][1] << " " << 
		w[1][0] << " " << 
		w[1][1] << std::endl;
#endif
		 

	out.assign(curves[ic1][ic2].getQ(),newI);
}

#define err() { cerr << fname << ": " << strerror(errno) << endl; close (f); return 1; } 
#define truncw() { \
	cerr << fname << ": truncated write" << endl;\
	close(f); return 1;\
}
#define check_write(x) {\
	n = write(f,&(x), sizeof(x));\
	if (n < 0) err(); \
	if (n != sizeof(x)) truncw(); \
}



int C12Map::dump(char const *fname)
{
	int	f = open(fname,O_WRONLY | O_CREAT | O_TRUNC,0644);
	if (f<0) return errno;

	int	n,e;

	check_write(c1min);
	check_write(c1max);
	check_write(c2min);
	check_write(c2max);

	check_write(c1samples);
	check_write(c2samples);

/* c[12]steps recalculated */

	int	s = curves[0][0].getSize();

	check_write(s);
	
	for (int ic1 = 0; ic1 < c1samples; ic1++)
		for (int ic2 = 0; ic2 < c2samples; ic2++) {
			vector<float> const &q = curves[ic1][ic2].getQ();
			int	w = q.size()*sizeof q[0];
			n = write(f,&q[0],w);
			if (n < 0) err();
			if (n != w) truncw();

			vector<float> const &I = curves[ic1][ic2].getI();
			n = write(f,&I[0],w);
			if (n < 0) err();
			if (n != w) truncw();
			
			/* XXX: no experimetal data, don't store errors */
		}
	if (close(f)) { err(); }
	else return 0;
}

#define truncr() { \
	cerr << fname << ": truncated write" << endl;\
	close(f); return 1;\
}

#define check_read(x) {\
	n = read(f,&(x), sizeof(x));\
	if (n < 0) err(); \
	if (n != sizeof(x)) truncr();\
}

int C12Map::restore(char const *fname)
{
	int	f = open(fname,O_RDONLY,0);
	if (f<0) {
		cerr << fname << ": " << strerror(errno) << endl;
		return errno;
	}

	int	n,e;

	float	min1,max1,min2,max2;
	int	samples1,samples2,s;

	check_read(min1);
	check_read(max1);
	check_read(min2);
	check_read(max2);

	check_read(samples1);
	check_read(samples2);

	setRange(min1,max1,samples1,min2,max2,samples2);

	check_read(s);
	vector<float>	q,I;

	q.resize(s);
	I.resize(s);
	int	r = s*sizeof q[0];

	curves.resize(c1samples);
	for (int ic1 = 0; ic1 < c1samples; ic1++) {
		curves[ic1].resize(c2samples);

		for (int ic2 = 0; ic2 < c2samples; ic2++) {
			n = read(f,&q[0],r);
			if (n < 0) err();
			if (n != r) truncr();

			n = read(f,&I[0],r);
			if (n < 0) err();
			if (n != r) truncr();

			curves[ic1][ic2].assign(q,I);
		}
	}

	close(f);
	return 0;
}

static void filetodir(const char *src,const char *dir,const char *dst)
{

	char	dname[PATH_MAX];
	sprintf(dname,"%s/%s",dir,dst);

	ifstream s(src); assert(!s.fail());
	ofstream d(dname); assert(!d.fail());

	s.seekg(0,s.end);
	long size = s.tellg();
	s.seekg(0);

	char	*buf = new char[size];

	s.read(buf,size); assert(! s.fail());
	d.write(buf,size); assert(! d.fail());

	s.close();
	d.close();
	delete [] buf;
}

void C12Map::lazyCurve(int ic1,int ic2)
{
	float	c1 = c1min + ic1*c1step,
		c2 = c2min + ic2*c2step;

	// sum_partial_profile
	// cp Profile -> Curve
	
	imp_profile->sum_partial_profiles(c1,c2);

	const Eigen::VectorXf & profI = imp_profile->get_intensities(),
	      profQ = imp_profile->get_qs();

	std::vector<float> q(profQ.size());
	std::vector<float> I(profI.size());

	for (unsigned int i=0; i<q.size(); i++) {
		q[i] = profQ[i];
		I[i] = profI[i];
	}

	curves[ic1][ic2].assign(q,I);
	curves[ic1][ic2].alignScale(*measured);
}



void C12Map::alignScale(Curve const &ref)
{
	float	qmin, qmax;
	int	steps;

	for (int ic1 = 0; ic1 < c1samples; ic1++)
		for (int ic2 = 0; ic2 < c2samples; ic2++)
			curves[ic1][ic2].alignScale(ref);
}

