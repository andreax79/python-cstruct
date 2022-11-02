#!/usr/bin/env sh
cd "$(dirname "$0")/.." || exit
python -m examples.flexible_array $*
