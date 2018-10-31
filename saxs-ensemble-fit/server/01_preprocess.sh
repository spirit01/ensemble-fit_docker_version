#!/bin/bash
set -u

source common
source config.server

if [ $# -ne 1 ]; then
	echo "Missing request id argument"
	exit "${RETURN_SERVER_ERROR}"
fi

request_id=$1
request_dir="${REQUESTS_DIR}/${request_id}"

source "${request_dir}/params.txt"

workdir="${request_dir}/workdir"
mkdir "${workdir}"
mkdir "${workdir}/structures"

# check & copy SAXS data
saxs_data="${request_dir}/saxs.dat"
delimiter='=============================================='

# If we have a rich saxs file, cut out only the relevant part of it
if grep -q "${delimiter}" "${saxs_data}"; then
	sed -n "/${delimiter}/,/${delimiter}/{/${delimiter}/b;/${delimiter}/b;p}" "${saxs_data}" > "${workdir}/saxs.dat"
else
	cp "${saxs_data}" "${workdir}/saxs.dat"
fi

err_msg=$(./saxs_test.py "${workdir}/saxs.dat" 2>&1)
[ $? -eq 0 ] || exit_error "${RETURN_USER_ERROR}" "SAXS data: ${err_msg}"


# extract NMR structures
structures_file="${request_dir}/${STRUCTURES_FILE}"
filetype="$(file -ib "${structures_file}" | sed 's/;.*//')"
case "${filetype}" in

	"application/zip")
		unzip -qj "${structures_file}" -d "${workdir}/structures"
	;;
	"application/gzip")
		tar -xzf "${structures_file}" --xform="s/\//_/" -C "${workdir}/structures"
	;;
	"application/x-bzip2")
		tar -xjf "${structures_file}" --xform="s/\//_/" -C "${workdir}/structures"
	;;
	"application/x-rar")
		unrar --extract-no-paths "${structures_file}" "${workdir}/structures" > /dev/null
	;;
	*)
		basefile="$(basename "${structures_file}")"
		extension="${basefile##*.}"
		if [ "${extension}" != "pdb" ] && [ "${extension}" != "PDB" ]; then
			exit_error "${RETURN_USER_ERROR}" "Unsupported structures archive type: ${filetype}"
		fi

		sed -n '/^MODEL/, /ENDMDL/ p' "${structures_file}" | csplit --quiet --elide-empty-files --prefix="${workdir}/structures/structure" --suffix-format="%04d.pdb"  - "/^MODEL/" "{*}"
	;;
esac

[ $? -eq 0 ] || exit_error "${RETURN_USER_ERROR}" "Failed to decompress structures file"

# delete all non-PDB files in the structures directory
for file in "${workdir}/structures/"*; do
	if ! [ -f "${file}" ] || ! [[ "${file}" = *.pdb || "${file}" = *.PDB ]]; then
		rm -rf "${file}"
	fi
done

# rename all structures to the scheme structureXXXX.pdb
index=1
tmpdir="$(mktemp -d)"
shopt -s nullglob
mv "${workdir}/structures/"* "${tmpdir}"
for file in "${tmpdir}/"*; do
	newfilename="$(printf "structure%04d.pdb" "${index}")"
	mv "${file}" "${workdir}/structures/${newfilename}"
	((index += 1))
done
rmdir "${tmpdir}"

[ "${index}" == "1" ] && exit_error "${RETURN_USER_ERROR}" "No valid PDB record found."

for file in "${workdir}/structures/"*; do
	if obabel -ipdb "${file}" -osdf 2>&1 | grep -q "^0 molecules converted$"; then
		exit_error "${RETURN_USER_ERROR}" "Provided PDB is invalid."
	fi
done

shopt -u nullglob

exit "${RETURN_OK}"
