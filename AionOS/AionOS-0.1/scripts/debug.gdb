# Use a GDB build with AArch64 support: gdb -x scripts/debug.gdb
set architecture aarch64
file build/aion.elf
target remote 127.0.0.1:1234
break kernel_main
continue
