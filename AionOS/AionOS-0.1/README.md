# AionOS 0.1

AionOS is an original, freestanding AArch64 operating system for QEMU's `virt`
board. It boots directly into its own C kernel, draws a native graphical login
screen and desktop, and runs its own File Manager and Text Editor. It contains
no Linux, BSD, Darwin/XNU, FreeRTOS, existing kernel framework, GUI toolkit, or
third-party operating-system code. QEMU and LLVM are host development tools.

This is a functional educational OS, with deliberately small limits. Its apps
are trusted kernel code, not isolated userspace processes. It is intended for
the prescribed virtual machine, not for booting physical Apple hardware.

## Build and run on an Apple Silicon Mac

Install Apple's Command Line Tools if they are not already present, then use
Homebrew to install the development tools:

```sh
xcode-select --install
brew install qemu llvm lld
cd ~/AionOS/AionOS-0.1
make
./run.sh
```

If Command Line Tools are already installed, skip the first command. Python 3
is used by the image and test utilities; the Command Line Tools normally provide
it. If it is missing, `brew install python` supplies it. Alternatively,
`./scripts/setup.sh` installs QEMU, LLVM and LLD and compiles the project.

The default launcher opens a native QEMU window using its Cocoa display backend.
The guest draws the display itself; Cocoa only presents QEMU's framebuffer on
macOS. Boot diagnostics also appear in the terminal. The login screen appears
after approximately 1.5 seconds. Click **Login**; no credentials are required.

The launcher creates a **new blank 4 MiB disk only when no disk exists** at
`data/aion-disk.img`. It preserves existing images. Saved files survive reboot,
QEMU exit and subsequent runs. Do not run two VMs against the same image.

```sh
./run.sh --ram-only       # No disk attached; edits last only for this boot
./run.sh --headless       # Serial diagnostics, no host display window
make clean               # Remove build products; data/aion-disk.img is preserved
make                     # Rebuild the freestanding ELF kernel
```

Use **Power > Shutdown** to stop the VM or close the QEMU window. Closing the
window loses edits that have not been saved. The Power menu asks before
discarding text in a modified editor. `Control+C` in the launching terminal
also stops QEMU. This runs one emulated Cortex-A57 CPU with TCG on the Apple
Silicon host; HVF is not enabled or claimed to be verified.

## Use the desktop

- Click the File Manager or Text Editor desktop icon, taskbar button, or
  Applications menu entry. About AionOS is also in the Applications menu.
- Drag a window's title bar. Clicking a window raises it and gives it keyboard
  focus. The `x` button closes it. Up to six windows can coexist.
- File Manager starts at `/`. Select a folder and click **Open**, press Enter,
  or double-click it. **Back** goes to its parent directory.
- **New File**, **New Folder** and **Rename** open a name dialog. Its initial
  text is selected, so typing replaces it. Control+A selects the dialog text.
  Enter accepts, Escape cancels. Delete asks for confirmation. Nonempty folders
  must be emptied before deletion. The four initial top-level folders are
  protected against rename and deletion.
- File Manager sorts folders before files. The Up/Down buttons, arrow keys, and
  tablet wheel events allow navigation through long lists.
- Select a text file and open it to launch an editor. Type printable ASCII,
  Enter for a newline, Tab for four spaces, Backspace or Delete to remove text.
  Arrows, Home, End and Page Up/Down move the caret. Click in the text to move
  the caret; Up/Down buttons and wheel events scroll. Long lines soft-wrap.
- **Save** writes the current file. **Save As** accepts a full absolute path
  such as `/Documents/Projects/ideas.txt`, or a filename placed in `/Documents`.
  The parent folder must already exist. Replacing another file asks first.
- Editor shortcuts: Control+S saves; Control+Shift+S opens Save As; Control+N
  opens a new document; Control+O opens a file by path; Control+A selects all
  text. Closing a modified document asks before discarding it.
- Two editor windows can open one file. If another editor saves different text,
  a stale editor's ordinary Save is refused; use Save As to keep its version.
- The taskbar shows the PL031 virtual RTC time in UTC. Login is a convenience
  transition, not authentication or a security boundary.

## Project map

```text
boot/                         AArch64 entry and ELF linker layout
kernel/
  arch/arm64/                 Exception vectors, context switch, PSCI power
  interrupts/                GICv2 and ARM virtual timer
  memory/                    Physical pages, free-list heap, identity MMU
  scheduler/                 Cooperative kernel tasks and stacks
  drivers/                   PL011, fw_cfg/ramfb, virtio MMIO/input/block
  fs/                        Original directory/file API and disk snapshots
  graphics/                  Clipped rectangles, original 5x7 font, cursor
  ui/                        Widgets, modal dialogs, windows, desktop
apps/
  file_manager/              Native folder and file operations
  text_editor/               Native editor, caret, soft wrap, scrolling
include/                     Clear kernel and application API contracts
scripts/                     Setup and GDB commands
tools/                       Image creation, inspection and QEMU tests
tests/                       Host-side filesystem tests and exception entry
build/                       Generated kernel, objects and verification output
data/                        Runtime disk image (created by run.sh)
docs/                        Architecture, development logs and screenshots
```

## Boot sequence

QEMU loads the ELF at `0x40080000` and enters `_start` without an external
bootloader. Secondary CPUs would park; the launcher deliberately selects one
CPU. If entered at EL2, the assembly grants counter access and drops to EL1h.
It masks exceptions, establishes a 64 KiB boot stack, clears BSS, preserves the
boot argument, and calls `kernel_main`.

The kernel brings up physical memory and the heap, verifies allocation/free,
enables its translation table, installs an aligned exception vector table,
configures GICv2, and verifies that the 100 Hz timer IRQ fires. It then configures
ramfb, creates the input queues, initializes or loads the filesystem, displays
boot diagnostics and transitions to login. Finally two cooperative tasks poll
input and run the desktop. After a desktop pass, the input task waits for the
next interrupt rather than continuously spinning.

The boot screen reports memory, translation, exceptions/timer, display, input,
filesystem and UI initialization. Serial output starts earlier, so a display
failure is still diagnosable. `docs/ARCHITECTURE.md` explains the hardware and
implementation in more detail.

## Memory and scheduling

Physical allocation uses a bitmap of 4 KiB pages beginning after the complete
kernel BSS and boot stack. A minimal FDT reader can obtain the memory size; the
bare ELF path can fall back to the prescribed 256 MiB layout. Do not change the
launcher's memory size below 256 MiB. The allocator caps its managed range at
256 MiB even if QEMU is given more RAM.

The 1 MiB heap uses 16-byte aligned first-fit blocks, splitting on allocation
and merging adjacent free blocks on free. Framebuffers, DMA buffers, filesystem
nodes and task stacks are statically reserved and do not overlap page allocation.

A 4 KiB-granule level-1 table identity-maps the low GiB as execute-never device
memory and the next GiB as normal uncached RAM. TTBR0, MAIR and TCR are configured
and SCTLR enables translation. Caches stay disabled to make guest/device DMA
coherence explicit and simple. This is basic virtual memory; there are no
per-process address spaces, demand paging, W^X enforcement or user isolation.

The scheduler holds up to eight kernel tasks, each with a 16 KiB stack. Yield
saves and restores x19-x30 and SP according to the AArch64 calling convention.
The timer does not preempt tasks. Applications use the documented C kernel APIs
in `include/`; they do not execute EL0 system calls or dynamically loaded binaries.

## Filesystem and persistence

The filesystem has 64 fixed nodes, including directories. Each text file holds
at most 4095 bytes and a trailing NUL; filenames hold at most 47 printable ASCII
characters. Directories have parent node IDs. The API validates parents, names,
duplicates, sizes and deletion of nonempty folders. Stable identities let an
editor notice deletion and reuse of its original node. Boot creates:

```text
/System/About.txt
/Applications/
/Documents/Welcome.txt
/Documents/Notes.txt
/Desktop/
```

When a writable, flush-capable virtio disk is present, the OS uses its own
little-endian snapshot format. Two 1 MiB slots hold a header and node payload.
Each has a generation number and CRC32 for both header and payload. A save
invalidates the inactive header, flushes, writes the payload, flushes, writes
the new header, and flushes again. The previous active snapshot is retained.
On boot, the newest structurally valid snapshot is selected; damage to it can
fall back to the other snapshot. CRCs detect corruption, not malicious edits.

Only images with both header sectors zero are initialized automatically.
Unrecognized nonzero headers are preserved and cause a visible RAM-only fallback.
Disk errors are reported; a failed save never produces the normal disk-saved
status. This scheme is small and intentionally rewrites the whole filesystem
per save. It is not a journaled, general-purpose filesystem.

Host inspection does not mount or modify the image:

```sh
python3 tools/disk.py
python3 tools/disk.py --cat /Documents/Welcome.txt
```

To experiment with a fresh disk, shut down QEMU, move `data/aion-disk.img` to a
backup name, then run the launcher to create a new one. `make clean` leaves it
alone.

## Graphics and hardware choices

The prescribed machine uses:

| Device | Guest use | Reason |
|---|---|---|
| PL011 at `0x09000000` | Serial logs and panic reports | Small, early MMIO console |
| GICv2 at `0x08000000` / `0x08010000` | IRQ routing | Simpler single-CPU controller |
| ARM virtual counter and PPI 27 | Timer and uptime | Architectural CPU interface |
| PL031 at `0x09010000` | UTC clock | One register gives seconds |
| fw_cfg at `0x09020000` + `ramfb` | 1024x768 XRGB8888 display | Guest-owned pixels, no GPU command language |
| Modern virtio MMIO slots at `0x0a000000` | Device discovery and queues | Avoids PCI enumeration |
| virtio keyboard | US ASCII keys and modifiers | No USB stack required |
| virtio tablet | Absolute pointer and left button | Natural host cursor mapping |
| virtio block | Persistent disk and flush | Compact DMA request protocol |
| PSCI via HVC | Reboot and poweroff | QEMU's board power interface |

The renderer draws into a back buffer with clipped rectangles and an original
5x7 font, then copies pixels into the ramfb buffer. It has no dependency on
X11, Wayland, SDL, Cocoa, Qt or a browser inside the guest. The mouse cursor,
buttons, window borders, title bars, dialogs and applications are guest code.
Windows repaint when input, filesystem state or the clock changes. The display
has fixed size; there is no accelerated compositor or host-window resize support.

Primary hardware references used during development:
[QEMU virt](https://www.qemu.org/docs/master/system/arm/virt),
[QEMU fw_cfg](https://www.qemu.org/docs/master/specs/fw_cfg.html),
[QEMU ramfb source](https://github.com/qemu/qemu/blob/master/hw/display/ramfb.c),
and [OASIS Virtio 1.2](https://docs.oasis-open.org/virtio/virtio/v1.2/virtio-v1.2.html).
These describe hardware protocols; the drivers and OS implementation here are original.

## Debugging and verification

```sh
make test                # Host filesystem checks with ASan and UBSan
make smoke               # Real QEMU GUI, persistence and power tests
make exception-check     # Deliberate abort in a separate test kernel
./run.sh --debug          # Pause at boot; GDB listens on localhost:1234
```

Connect an AArch64-capable GDB from the project directory:

```sh
gdb -x scripts/debug.gdb
```

GDB is optional and not required for building or running. These commands require
a GDB build with AArch64 support; no GDB installation or connection is claimed
as part of this project's verification. Useful breakpoints include
`kernel_main`, `exception_fatal`, `irq_dispatch` and `context_switch`.
The ELF retains symbols and DWARF debug information. `build/aion.map` gives the
link layout. LLVM's `llvm-objdump` can disassemble the freestanding ELF.

A fatal exception reports PC, SP, ESR_EL1, FAR_EL1, SPSR_EL1 and x0-x30 on serial,
then masks interrupts and halts. The display shows the exception reason, PC, SP, ESR and FAR when graphics
are available. Ordinary panics and assertions also use both outputs. The separate
exception test intentionally writes to an unmapped virtual address and verifies
the handler; it does not alter the normal OS image.

`make smoke` boots the real guest headlessly, sends virtio keyboard/tablet events
through QEMU, captures actual framebuffer screenshots, and checks the resulting
disk contents. It exercises login, simultaneous apps, window dragging, folder
creation/deletion, file creation, edit, Save, Save As, rename, delete, reopen,
disk reload, GUI reboot/shutdown, snapshot corruption fallback and RAM-only boot.
It uses temporary disks and never changes `data/aion-disk.img`.
Logs and screenshots are written to `build/verification/`.

See `docs/VERIFICATION.md` for the verified platform and limits, and
`docs/MILESTONES.md` for the incremental development record.

## Current limitations and roadmap

The running features above are implemented; there are no fake application
screens. This remains a compact learning OS rather than a production system:

- One CPU; cooperative tasks; trusted in-kernel applications and shared RWX RAM.
- Fixed virtual hardware, 256 MiB managed RAM, 1024x768 display, US ASCII layout.
- Six windows; no minimizing, resizing, clipboard, selection ranges, undo,
  Unicode, font shaping or terminal app. Editor Control+A selects all only.
- Filesystem limit of 64 entries and 4095 bytes per file; no moves across folders,
  symbolic links, permissions, mounting other filesystems or disk expansion.
- Snapshot persistence is synchronous; large numbers of edits and writes are
  not tuned. No claim of exhaustive fault-injection or hardware durability testing.
- No network, audio, USB, SMP, real Mac boot, EL0 executables or POSIX layer.
- Automated screenshots and inputs validate the QEMU device path; they do not
  establish support for every host keyboard, pointing device or QEMU version.

Next steps can be implemented separately while keeping boot tests passing:
smaller page mappings with executable/read-only permissions; cache maintenance
for DMA; ELF loading and isolated EL0 processes; preemptive scheduling; scalable
block allocation; larger files; undo and text selection; window resize; and a
virtio GPU backend. None of these are represented as implemented features.
