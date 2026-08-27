#!/usr/bin/env bash
set -euo pipefail

TARGET_DIR="/home/lsc18/carhack-targets/iso14229"
LOG_DIR="/home/lsc18/carhack-uds-fuzzing/logs"

mkdir -p "$LOG_DIR"
cd "$TARGET_DIR"

date --iso-8601=seconds | tee "$LOG_DIR/execution-time.log"
git rev-parse HEAD | tee "$LOG_DIR/target-commit.log"
bazel --version | tee "$LOG_DIR/bazel-version.log"

CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel build //fuzz:fuzz_server \
  2>&1 | tee "$LOG_DIR/baseline-fuzz-build.log"

CC=/usr/bin/clang-18 \
CXX=/usr/bin/clang++-18 \
bazel test //fuzz:fuzz_server \
  --test_output=all \
  --test_timeout=120 \
  --nocache_test_results \
  2>&1 | tee "$LOG_DIR/baseline-fuzz-run.log"

cp bazel-testlogs/fuzz/fuzz_server/test.log \
  "$LOG_DIR/baseline-fuzz-detail.log"

sha256sum "$LOG_DIR/baseline-fuzz-detail.log" \
  | tee "$LOG_DIR/baseline-fuzz-detail-hash.log"
