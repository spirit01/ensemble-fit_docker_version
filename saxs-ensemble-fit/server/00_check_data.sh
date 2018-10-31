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
if ! [ -d "${request_dir}" ]; then
	echo "Request directory does not exist: \"${request_dir}\"!"
	exit "${RETURN_SERVER_ERROR}"
fi

request_params="${request_dir}/params.txt"
[ -f "${request_params}" ] || exit_error "${RETURN_SERVER_ERROR}" "No request parameters file: \"${request_params}\"!"

source "${request_params}"

structures_file="${request_dir}/${STRUCTURES_FILE}"
[ -f "${structures_file}" ] || exit_error "${RETURN_SERVER_ERROR}" "Cannot read structures archive: \"${structures_file}\"!"

saxs_data="${request_dir}/saxs.dat"
[ -f "${saxs_data}" ] || exit_error "${RETURN_SERVER_ERROR}" "No SAXS data provided: \"${saxs_data}\"!"

exit "${RETURN_OK}"
