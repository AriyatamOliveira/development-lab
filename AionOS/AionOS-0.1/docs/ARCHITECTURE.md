# Architecture notes for students

Read `boot/start.S`, `kernel/main.c`, then the subsystem headers in that order.
The C entry makes the dependencies visible: memory before translation, vectors
before unmasking IRQs, graphics before desktop, filesystem before applications,
and scheduler contexts before entering task loops.

## CPU exceptions

AArch64's vector base must be aligned to 2048 bytes. Each of 16 vector slots is
128 bytes, covering current/lower exception levels and synchronous/IRQ/FIQ/SError
classes. The synchronous paths reach one fatal handler. The IRQ path saves all
integer registers plus ELR and SPSR in a 272-byte, 16-byte-aligned frame. It reads
GIC IAR, rearms the timer for IRQ 27, writes EOI, restores the frame and executes
`eret`. FIQ and SError are fatal in this first implementation. SIMD is excluded
from generated C by `-mgeneral-regs-only`, so no floating-point register context
is silently omitted. IRQs update a counter and do not call the allocator or UI.

## Scheduler boundary

`task_yield()` runs at an ordinary C call boundary. Only the ABI's callee-saved
integer registers and SP must survive this call; caller-saved registers belong
to the yielding function's normal compiler-generated spills. A newly created
context points its x30 at `task_start`, which invokes the task and retires it if
it returns. The two real tasks share an address space, not a stack. This is a
cooperative thread abstraction; it does not pretend that GUI windows are isolated
processes. A non-yielding task could monopolize the CPU, while timer IRQs still fire.

## DMA ownership

Virtio queues use descriptor, available and used rings. The driver negotiates
only `VERSION_1` and the block features it understands. Every queue address is
physical because the address map is identity. Descriptors and buffers are
aligned, memory is uncached, and `dsb sy` barriers enforce publication order.
A device can write only to buffers described as device-writable. Input buffers
are recycled after consuming the used ring; each queue has 64 entries.

The block driver submits one request at a time. A permanent bounce buffer owns
its payload; the header and status also have permanent storage. A timeout marks
the device failed. A late device write therefore cannot target a returned stack
frame or a freed heap allocation. The persistent snapshot layer requires an
explicit successful device flush rather than claiming that a RAM write is a
durable save.

## GUI ownership

The input driver translates hardware events into a bounded event ring. Each key
event carries its modifier state. The desktop consumes this queue, routes keys
to the focused application, manages modal dialogs and drag state, and repaints
the back buffer when dirty. A window owns its application state allocation;
closing it frees that allocation. Six stable window records back a stacking
order. Dialogs are modal so their window callbacks cannot lose the owner to a
simultaneous click on another window's close button.

File Manager is a filesystem API client. It refreshes listings when the global
filesystem revision changes. Text Editor holds a private document buffer, a
file identity and a hash of the last saved version. An ordinary Save checks
that another editor has not changed the file since that version. The file API
and graphics primitives are clear in-kernel APIs, not an implied syscall ABI.

## Snapshot layout

All disk integers are little-endian; the guest is little-endian AArch64. Slot 0
starts at sector 0 and slot 1 at sector 2048. Each slot begins with a 512-byte
header followed by the fixed node table, rounded up to a sector boundary.

| Header offset | Field |
|---|---|
| 0 | Eight bytes: `AIONFS1` followed by NUL |
| 8 | u32 format version (1) |
| 12 | u32 node-table byte length |
| 16 | u32 CRC32 of the unpadded node table |
| 20 | u32 reserved (0) |
| 24 | u64 nonzero generation |
| 32 | u32 CRC32 of header bytes 0..31 |
| 36 | Zero padding to 512 bytes |

Each node occupies 4156 bytes: used u8, directory u8, parent u16, length u32,
identity u32, name[48], data[4096]. Sixty-four nodes occupy 265984 bytes;
266240 bytes are transferred to cover whole sectors. The importer validates
root type, bounds, terminators, parents, cycles, unique names and identities
before replacing live state. This simple fixed representation is versioned and
has a compile-time size check in the persistence layer.

CRC validation and header-last publication are useful here because a prior
snapshot remains intact throughout a save. They are not a replacement for
application-level backups, filesystem security or comprehensive crash testing.
