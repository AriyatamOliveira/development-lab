#include "virtio.h"
static VDevice device;
static bool ready;
static uint64_t capacity;
static struct {
    uint32_t type, reserved;
    uint64_t sector;
} request __attribute__((aligned(16)));
static volatile uint8_t status;
// A permanently allocated bounce buffer also keeps a timed-out DMA request
// from ever overwriting a caller's stack or a subsequently freed allocation.
static uint8_t bounce[512 * 1024] __attribute__((aligned(4096)));
static void found(uintptr_t base, unsigned id) {
    if (id != 2 || ready)
        return;
    if (!virtio_init(&device, base, (1u << 9) | (1u << 5)) || !virtio_queue(&device, 0))
        return;
    if (device.features & (1u << 5))
        return;
    capacity = mmio_read(base + 0x100) | ((uint64_t)mmio_read(base + 0x104) << 32);
    virtio_ready(&device);
    ready = true;
}
bool block_init(void) {
    virtio_scan(found);
    return ready;
}
bool block_ready(void) {
    return ready;
}
uint64_t block_capacity(void) {
    return capacity;
}
static bool execute(unsigned type, uint64_t sector, uint32_t bytes) {
    if (!ready)
        return false;
    VQueue *q = &device.q[0];
    request.type = type;
    request.sector = sector;
    status = 255;
    q->desc[0] = (struct VDesc){(uintptr_t)&request, sizeof request, 1, bytes ? 1 : 2};
    if (bytes)
        q->desc[1] =
            (struct VDesc){(uintptr_t)bounce, bytes, (uint16_t)(1 | (type == 0 ? 2 : 0)), 2};
    q->desc[2] = (struct VDesc){(uintptr_t)&status, 1, 2, 0};
    virtio_submit(&device, 0, 0);
    uint64_t deadline = millis() + 3000;
    while (q->seen == q->used.idx) {
        barrier();
        if (millis() > deadline) {
            ready = false;
            mmio_write(device.base + 0x70, 128);
            boot_log("[DISK] DMA timeout; device disabled");
            return false;
        }
    }
    barrier();
    unsigned id = q->used.ring[q->seen % VQ_SIZE].id;
    q->seen++;
    uint32_t irq = mmio_read(device.base + 0x60);
    if (irq)
        mmio_write(device.base + 0x64, irq);
    return id == 0 && status == 0;
}
bool block_transfer(bool write, uint64_t sector, void *data, uint32_t bytes) {
    if (!bytes || bytes % 512 || bytes > sizeof bounce || sector > capacity ||
        bytes / 512 > capacity - sector)
        return false;
    if (write)
        memcpy(bounce, data, bytes);
    if (!execute(write ? 1 : 0, sector, bytes))
        return false;
    if (!write)
        memcpy(data, bounce, bytes);
    return true;
}
bool block_flush(void) {
    return ready && (device.features & (1u << 9)) && execute(4, 0, 0);
}
