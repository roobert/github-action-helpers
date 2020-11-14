#!/usr/bin/env bash
set -euo pipefail

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

REGION="${1}"
ENVIRONMENT="${2}"
DEPLOYMENT="${3}"
TARGET="${4:-k8s_and_infra}"
STAGE="${5:-plan}"
BRANCH="${6:-master}"

${DIR}/workflow-trigger.py \
  -r "${REGION}" \
  -e "${ENVIRONMENT}" \
  -d "${DEPLOYMENT}" \
  --target "${TARGET}" \
  --stage "${STAGE}" \
  --branch "${BRANCH}"

${DIR}/workflow-query.py \
  -r "${REGION}" \
  -e "${ENVIRONMENT}" \
  -d "${DEPLOYMENT}" \
  --target "${TARGET}" \
  --stage "${STAGE}" \
  --branch "${BRANCH}" \
  --logs

