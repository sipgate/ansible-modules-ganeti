#!/bin/bash

set -e

if [ $# -eq 1 ]; then
    echo "Changing working directory to $1"
    cd $1
fi

echo "* Pulling latest ganeti-docker image"
docker pull ghcr.io/sipgate/ganeti-docker:latest

echo "* Starting ganeti-docker container in detached mode"
docker run --name ganeti_vcluster --detach --publish 5080:5080 --cap-add=NET_ADMIN ghcr.io/sipgate/ganeti-docker:latest

echo "* Waiting for vcluster setup to finish (max. 60 seconds)"
n=0; until [ "$n" -ge 60 ]; do curl --output /dev/null --silent --fail --insecure https://localhost:5080/2/info && break; n=$((n+1)); sleep 5; done

echo "* Test-Connect to Ganeti RAPI"
curl --insecure https://localhost:5080/2/info
echo

echo "* Executing Python tests"
pytest -vv

echo "* Stop ganeti-docker container"
docker stop ganeti_vcluster
