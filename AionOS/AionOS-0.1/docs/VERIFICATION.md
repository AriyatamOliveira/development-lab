# Verification record

Verified on 2026-10-01 on an arm64 macOS 27.0.1 host with Homebrew LLVM/LLD
22.1.3 and QEMU 11.1.2. All guest runs used the original freestanding ELF,
QEMU `virt,gic-version=2`, one emulated Cortex-A57 CPU, TCG and 256 MiB RAM.
The image is a statically linked little-endian AArch64 ELF, entry `0x40080000`,
with debug information and no dynamic interpreter or host system libraries.

## Checks completed

- Compiled and booted every development milestone; the historical serial logs
  and selected screenshots are in this folder.
- Rebuilt the final source from clean build products with warnings as errors.
- Host runtime/heap/filesystem tests passed with AddressSanitizer and
  UndefinedBehaviorSanitizer. They cover word-copy alignment and bounds,
  allocation exhaustion and coalescing, file lifecycle, path navigation,
  duplicates, directory deletion constraints, malformed imports, name/size
  limits and entry exhaustion.
- QEMU GUI regression passed using actual virtio keyboard and tablet events:
  login, folder navigation/creation/deletion, file creation, text entry,
  Home/End/Backspace edits, Save, Save As, rename, delete, reopen, two
  simultaneous applications, title-bar dragging and dirty-close dialogs.
- The GUI reboot reached a second complete boot in the same QEMU process and
  reloaded the persistent filesystem. GUI shutdown exited QEMU successfully.
- A new QEMU process reopened the saved text. Host snapshot inspection checked
  its exact bytes, not just a saved-status message or screenshot.
- Corrupting the newest snapshot payload caused the guest to load the older
  validated generation. A no-disk boot selected the explicit RAM filesystem.
- A separate kernel intentionally caused a real ARM64 translation data abort.
  The report included PC, SP, ESR_EL1, FAR_EL1, SPSR_EL1 and x0-x30. The guest
  then halted, with the key values also visible in its graphical panic panel.
- The native Cocoa QEMU display backend booted successfully and its guest
  accepted the login action. QEMU framebuffer captures verified visible output.
- Shell syntax and Python source compilation checks passed. The disk utility
  uses exclusive creation and does not truncate existing images. The clean
  command deletes build products while persistent data lives separately.

Current final serial logs and actual QEMU screenshots are in `verification/`.
The test tools regenerate equivalent evidence under `build/verification/`.

## Boundaries

These checks establish a functional small OS on the specified QEMU device set.
They do not establish physical Mac boot, HVF support, preemptive/user-isolated
processes, different machine models, expanded RAM layouts, arbitrary host input
layouts, exhaustive power-loss recovery or production security. GDB commands
are supplied, but an actual GDB connection was not part of this verification.

Persistent storage has 64 entries including directories and 4095 bytes per file.
Applications share the kernel address space; the scheduler is cooperative.
See the README for the complete limits and roadmap.
