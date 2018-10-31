#!/bin/bash
set -u

source common
source config.server

while true; do
	for dir in $(find "${REQUESTS_DIR}" -mindepth 2 -maxdepth 2 -type d); do
		if [ "$(cat "${dir}/status.txt")" == "accepted" ]; then
			set -- $(echo "${dir}" | tr / '\012' | tail -2)
			request_id="$1/$2"
			echo "started" > "${dir}/status.txt"
			log_info "$request_id: Request processing started"
			./process_request.sh "${request_id}" &
		fi
	done
	sleep "${CHECK_FOR_REQUESTS_INTERVAL}"
done
