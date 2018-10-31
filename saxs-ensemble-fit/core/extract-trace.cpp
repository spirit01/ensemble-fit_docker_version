#include <sys/types.h>
#include <sys/stat.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <fcntl.h>
#include <iostream>
#include <vector>

using namespace std;

int main(int argc, char **argv)
{
	long	step;
	bool	getchi = false;
	int 	type,num,opt,wi = -1;

	while ((opt = getopt(argc,argv,"w:n:abrc")) != EOF) switch (opt) {
		case 'a': type = 'A'; break;
		case 'b': type = 'B'; break;
		case 'r': type = 'R'; break;
		case 'c': getchi = true; break;
		case 'n': num = atoi(optarg); break;
		case 'w': wi = atoi(optarg); break;
	}

	int	trace = open(argv[optind],O_RDONLY,0);

	vector<float>	w;
	w.resize(num);

	struct {
		float	c1,c2,chi2;
		int32_t	s;
	} s;

	int	recsiz = num * sizeof(float) + sizeof(s);

	step = 0;
	while (read(trace,&w[0],num * sizeof(float)) > 0) {
		read(trace,&s,sizeof(s));
		step++;


		if (s.s == type) {
			cout << step << ": ";
			if (getchi) cout << s.chi2 << " ";
			if (wi >= 0) cout << w[wi] << " "; 
			cout << endl;
		}
	}
}
