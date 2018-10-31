#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>
#include <sstream>

using namespace std;

int	ppos(int num,int steps,int pos[])
{
	int	ppos = 0,m = 1;

	for (int i=0; i<num; i++) {
		ppos += pos[i] * m;
		m *= steps;
	}

	return ppos;
}

int main(int argc, char **argv)
{
	int	num = 3,
		sel = 1;	/* XXX */
	float	step = .01;

	int	c;
	char	*os = 0;

	while ((c = getopt(argc,argv,"s:l:n:o:")) != -1) switch (c) {
		case 's': step = atof(optarg); break;
		case 'l': sel = atoi(optarg); break;
		case 'n': num = atoi(optarg); break;
		case 'o': os = strdup(optarg); break;
		default: cerr << "usage: " << argv[0] << " -s step -l select -n num" << endl;
			 return 1;
	}

	float	other[num];

	if (os) {
		for (char *p = os; *p; p++) if (*p == ',') *p = ' ';
		istringstream	s(os);

		for (int i=0; i<num; i++) {
			if (i==sel) i++;
			s >> other[i];
		}
	}

	int	steps = 1./step + 1;
	int	size = 1;

	for (int i=0; i<num; i++) size *= steps;
	float	*min = new float[size];

	for (int i=0; i<size; i++) min[i] = 9.99999e37;

	char	line[8000];

	while (! cin.getline(line,sizeof line).eof()) {
		istringstream	parse(line);

		float	w[num],c1,c2,chi;
		for (int i=0; i<num; i++) parse >> w[i];

		parse >> c1 >> c2 >> chi;

		int	pos[num];

		for (int i=0; i<num; i++) {
			pos[i] = w[i]/step;
		}
		int p = ppos(num,steps,pos);
		if (min[p] > chi) {
			min[p] = chi;
			cerr << p << " " << chi << endl;
		}
	}

	int	pos[num];
	for (int i=0; i<num; i++) pos[i] = other[i]/step;

	for (int i=0; i<steps; i++) {
		pos[sel] = i;
		int 	p = ppos(num,steps,pos);
		cout << (min[p] < 9e37 ? min[p] : 0. ) << endl;
	}
	return 0;
}
