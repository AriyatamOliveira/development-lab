#!/usr/bin/env bash
set -euo pipefail
if ! command -v brew >/dev/null; then echo 'Install Homebrew from https://brew.sh first.' >&2; exit 1; fi
brew install qemu llvm lld
cd "$(dirname "$0")/.."
make
