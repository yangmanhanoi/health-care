#!/bin/bash
# wait-for-db.sh - Wait for database to be ready

set -e

host="$1"
port="$2"
db_type="$3"
shift 3
cmd="$@"

echo "Waiting for $db_type database at $host:$port..."

until nc -z "$host" "$port"; do
  echo "Database is unavailable - sleeping"
  sleep 2
done

echo "Database is up - executing command"
exec $cmd
