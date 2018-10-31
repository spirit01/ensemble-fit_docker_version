VPATH=.:../bobyqa

UNAME=$(shell uname)

CXX=mpicxx
FC=mpif77

BOOSTOPT=-lboost_program_options
LAPACK=-llapack

FLIB?=-lgfortran
EXTRA=-g3

BOOSTINC=-I${BOOST}/include

ifeq (${DEBUGGING_SYMBOLS}, YES)
OPT=-O0 -g
else
OPT=-O2
endif

SRC:=Curve.cpp C12Map.cpp MinChi.cpp BruteForce.cpp RandomWalk.cpp MonteCarlo.cpp STunel.cpp GdMin.cpp Result.cpp main.cpp calfun.cpp

BOBJ:=bobyqa.o bobyqb.o prelim.o trsbox.o update.o altmov.o rescue.o

OBJ:=${SRC:.cpp=.o}  ${BOBJ}

CXXFLAGS=${EXTRA} ${OPT} ${BOOSTINC} -I /usr/include/eigen3 -std=c++11 
FFLAGS=${EXTRA} ${OPT}

IMPLIB= -limp_saxs -limp_kernel 

# FIXME:  parse-map extract-trace se nelinkuji s imp
# default: ensamble-fit parse-map extract-trace

default: ensamble-fit 

ensamble-fit: ${OBJ}
	${CXX} ${LDFLAGS} -o $@ ${OBJ} ${IMPLIB} ${FLIB}

parse-map: parse-map.o Curve.o C12Map.o
	${CXX} ${LDFLAGS} -o $@ parse-map.o Curve.o C12Map.o

test-fit: test-fit.o Curve.o
	${CXX} ${LDFLAGS} -o $@  test-fit.o Curve.o

test-ipol: test-ipol.o Curve.o C12Map.o
	${CXX} ${LDFLAGS} -o $@   test-ipol.o Curve.o C12Map.o

1dcut minc12 extract-trace: %: %.o
	${CXX} ${LDFLAGS} -o $@ $@.o

bobyqa-logreduce: %: %.o
	${CXX} ${LDFLAGS} -o $@ $@.o ${BOOSTOPT} ${LAPACK}

clean:
	rm -f ${OBJ} ensamble-fit

depend:
	touch .depend
	makedepend -f .depend -- $(CXXFLAGS) -- ${SRC}

-include .depend

# test
# DO NOT DELETE
