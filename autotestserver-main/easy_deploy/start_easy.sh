#!/usr/bin/env sh
set -eu
cd "$(dirname "$0")"
docker compose -f docker-compose.easydeploy.yml up -d --build
printf '\nEasy deploy started.\n'
