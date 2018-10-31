#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <iostream>
#include <sstream>

using namespace std;


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

	float	other[num+2];

	if (os) {
		for (char *p = os; *p; p++) if (*p == ',') *p = ' ';
		istringstream	s(os);

		for (int i=0; i<num+2; i++) s >> other[i];
	}
	else {
		cerr << "-o required" << endl;
		return 1;
	}

	int	steps = 1./step;

	float	chi[steps],dist[steps];

	for (int i=0; i<steps; i++) {
		chi[i] = 0.;
		dist[i] = 100*step*step;
	}
	
	char	line[8000];

	while (! cin.getline(line,sizeof line).eof()) {
		istringstream	parse(line);

		float	w[num],c1,c2,chi1;
		for (int i=0; i<num; i++) parse >> w[i];

		parse >> c1 >> c2 >> chi1;

		for (int j=0; j<steps; j++) {
			other[sel] = j * step;

			float d = 0,d2;
			for (int k=0; k<num; k++) {
				d2 = w[k] - other[k];
				d += d2*d2;
			}

			d2 = c1 - other[num];
			d += d2*d2;
			d2 = c2 - other[num+1];
			d += d2*d2;

			if (d < dist[j]) {
				dist[j] = d;
				chi[j] = chi1;
			}
		}
	}

	for (int i=0; i<steps; i++) cout << chi[i] << endl;

	return 0;
}
