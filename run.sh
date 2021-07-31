#!/bin/bash

set -e

cmd=$1

docker run -it --rm \
  -e WORKSPACE=${WORKSPACE} \
  -v ${WORKSPACE}:${WORKSPACE} \
  enclarify/lab-assistant-utils:1.0.0 ${cmd}
