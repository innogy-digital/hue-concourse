#!/usr/bin/env bash

export CONCOURSE_USERNAME=viewer
export CONCOURSE_PASSWORD=

cd $(dirname $0)
npm run start
