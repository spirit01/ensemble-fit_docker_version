#!/bin/bash
set -u
set -x 

module add openmpi-1.8.2-intel

source "${storage_dir}/config.server"
source "${storage_dir}/requests/${request_id}/params.txt"

request_dir="${storage_dir}/requests/${request_id}"
request_workdir="${storage_dir}/requests/${request_id}/workdir"

# copy application
cp "${storage_dir}/ensamble-fit" "${SCRATCHDIR}" || exit 1
cp "${storage_dir}/foxs" "${SCRATCHDIR}" || exit 1

# copy required data
cp "${request_workdir}/structures/"*.pdb "${SCRATCHDIR}" || exit 1
cp "${request_workdir}/saxs.dat" "${SCRATCHDIR}" || exit 1

cd "${SCRATCHDIR}" || exit 1

# perform optimization

structures_count="$(find . -name '*.pdb' | wc -l)"

PATH=${SCRATCHDIR}:$PATH
TMPDIR=${SCRATCHDIR}
export TMPDIR

do_work() {
	if [ -f results ]; then
		cp results results.work
		count=$(tail -n+2 results.work | wc -l)
		mkdir ComputedCurves
		cd ComputedCurves
		for i in `seq 1 "${count}"`; do
			e=$(awk -F "," -v i="${i}" 'NR == i + 1{print $2}' ../results.work)
			w=$(awk -F "," -v i="${i}" 'NR == i + 1{print $3}' ../results.work)
			mkdir "${i}"
			cd "${i}"
			ln -s ../../saxs.dat .
			for j in `seq 1 "${structures_count}"`; do
				n=$(printf %02d "${j}")
				ln -s "../../structure00${n}.pdb" .
				foxs -e "${e}" -w "${w}" "structure00${n}.pdb" saxs.dat
				awk '$1 !~ /^#.*$/ {print $1" "$3" 0.0"}' "structure00${n}_saxs.dat" > "final_m${j}.pdb.dat"
				rm structure*
			done
			rm saxs.dat
			cd ..
		done
		cd ..
		tar cf ComputedCurves.tar ComputedCurves/*
		mv ComputedCurves.tar "${request_dir}"
		mv results.work "${request_dir}/results"
		rm -rf ComputedCurves
	fi
}

mpirun ./ensamble-fit -n "${structures_count}" -m saxs.dat -a "${OPTIM_ALGORITHM}" -s "${OPTIM_STEPS}" -y "${OPTIM_SYNC}" -l "${OPTIM_ALPHA}" -b "${OPTIM_BETA}" -g "${OPTIM_GAMMA}"  -L -p structure00

retval="$?"
[ "${retval}" == "0" ] || exit "${retval}"

# Now we are finished with optimization, just process the final data
do_work
retval="$?"

# clean things up
rm -rf "${SCRATCHDIR}/"*

exit "${retval}"
