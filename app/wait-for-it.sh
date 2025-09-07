#!/usr/bin/env bash
# wait-for-it.sh

set -e

host="$1"
shift
cmd="$@"

until pg_isready -h "$host" > /dev/null 2>&1; do
  echo "Waiting for database at $host..."
  sleep 2
done

exec $cmd