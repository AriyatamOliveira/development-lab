# Incremental development record

The project was built and booted in stages on an Apple Silicon macOS host using
LLVM/LLD and QEMU 11.1.2. Serial logs captured during each stage are included.
This records development checks, not ten separate binaries to maintain.

| Milestone | Implemented and verified | Evidence |
|---|---|---|
| 1 | ELF entry, BSS/stack, original serial driver | `milestone-1.log` |
| 2 | Page allocator, heap, MMU, vector/GIC setup, live timer IRQs | `milestone-2.log` |
| 3 | fw_cfg DMA configuration, real ramfb pixels, original font | `milestone-3.log`, `milestone-3.png` |
| 4 | Virtio keyboard, tablet motion and button events | `milestone-4.log` |
| 5 | Cooperative stack switching, windows and dragging | `milestone-5.log`, `milestone-5-drag.png` |
| 6 | Login button transition to desktop | `milestone-6.log`, `login.png`, `desktop.png` |
| 7 | Directory/text API, default files and host lifecycle/limit tests | `milestone-7.log` |
| 8 | Native File Manager creation workflow | `milestone-8.log`, `milestone-8.png` |
| 9 | Native editor typing, Save As and RAM file save | `milestone-9.log`, `milestone-9.png` |
| 10 | Original disk snapshots and file reload in a new QEMU process | `milestone-10-save.log`, `milestone-10-reload.log`, `persistent.png` |

Final regression tests extend these checks to rename, deletion, simultaneous
apps, caret editing, unsaved close, native GUI power commands, full reboot,
corrupted-newest-snapshot fallback and no-disk boot. Run `make test`, `make smoke`
and `make exception-check` to regenerate current verification evidence.
