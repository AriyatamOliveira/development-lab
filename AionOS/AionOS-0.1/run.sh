#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
QEMU="${QEMU:-$(command -v qemu-system-aarch64 || true)}"
if [[ -z "$QEMU" && -x /opt/homebrew/bin/qemu-system-aarch64 ]]; then QEMU=/opt/homebrew/bin/qemu-system-aarch64; fi
if [[ -z "$QEMU" ]]; then echo 'QEMU is missing. Run: brew install qemu llvm lld' >&2; exit 1; fi
DISPLAY_BACKEND=cocoa
[[ "$(uname -s)" != Darwin ]] && DISPLAY_BACKEND=gtk
EXTRA=()
DISK=true
while [[ $# -gt 0 ]]; do
 case "$1" in
 --debug) EXTRA+=(-S -gdb tcp:127.0.0.1:1234) ;;
 --headless) DISPLAY_BACKEND=none ;;
 --ram-only) DISK=false ;;
 --help) echo 'Usage: ./run.sh [--debug] [--headless] [--ram-only]'; exit 0 ;;
 *) echo "Unknown option: $1" >&2; exit 1 ;;
 esac
 shift
done
make --no-print-directory
if $DISK; then
 python3 tools/mkdisk.py data/aion-disk.img
 EXTRA+=(-drive if=none,id=storage,format=raw,file=data/aion-disk.img -device virtio-blk-device,drive=storage)
fi
echo 'Starting AionOS. Close the QEMU window or use Power > Shutdown to exit.'
exec "$QEMU" -name AionOS -machine virt,gic-version=2 -cpu cortex-a57 -accel tcg \
 -smp 1 -m 256M -kernel build/aion.elf -global virtio-mmio.force-legacy=false \
 -device ramfb -device virtio-keyboard-device -device virtio-tablet-device \
 -display "$DISPLAY_BACKEND" -serial stdio -monitor none "${EXTRA[@]}"
