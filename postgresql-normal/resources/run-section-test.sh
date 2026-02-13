#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: $0 <section-path>"
  echo "Example: $0 ../ch01-getting-started/sec02-psql-crud-basics"
  exit 1
fi

SECTION_PATH="$1"

docker exec -i pg-learning psql -U postgres -d postgres < "${SECTION_PATH}/solution.sql"
docker exec -i pg-learning psql -U postgres -d postgres < "${SECTION_PATH}/test.sql"

echo "Section test passed: ${SECTION_PATH}"
