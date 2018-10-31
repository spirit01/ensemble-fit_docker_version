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

[ "${CLEAN_AFTER_SUCCESS}" = "false" ] && exit "${RETURN_OK}"

# renew kerberos ticket
kinit -R "${KERBEROS_PRINCIPAL}"

# clean things in /storage
if ! ssh "${STORAGE_USER}@${STORAGE_SERVER}" rm -rf "saxsfit/requests/${request_id}"; then
	exit_error "${RETURN_SERVER_ERROR}" "Cannot cleanup files on the storage"
fi

# clean local things
rm -rf "${request_dir}/workdir" || exit_error "${RETURN_SERVER_ERROR}" "Cannot cleanup local files in the request directory"

exit "${RETURN_OK}"
