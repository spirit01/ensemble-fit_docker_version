#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <limits.h>

#include <iostream>

#include "C12Map.h"

using namespace std;

static void usage(char const *);

int main(int argc,char **argv)
{
	char	prefix[PATH_MAX] = "", buf[PATH_MAX];

	int	opt, num = -1;

	C12Map	map;

	while ((opt = getopt(argc,argv,"n:")) != EOF) switch (opt) {
		case 'n': num = atoi(optarg); break;
		default: usage(argv[0]); return 1;
	}

	if (num < 0) { usage(argv[0]); return 1; }

	snprintf(buf, sizeof buf, "%s%02d/%02d_%%.2f_%%.3f.dat",prefix,num,num);
	if (map.load(buf)) return 1;

	snprintf(buf, sizeof buf, "%s%02d.c12",prefix,num);
	if (map.dump(buf)) return 1;

	return 0;
}


static void usage(char const *n)
{
	cerr << "usage: " << n << "-n num" << endl;
}
