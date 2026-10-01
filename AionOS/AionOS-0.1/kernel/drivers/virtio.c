#include "virtio.h"
void virtio_scan(void (*fn)(uintptr_t, unsigned)) {
    for (unsigned i = 0; i < 32; i++) {
        uintptr_t b = 0x0a000000UL + i * 0x200;
        if (mmio_read(b) == 0x74726976 && mmio_read(b + 8))
            fn(b, mmio_read(b + 8));
    }
}
bool virtio_init(VDevice *d, uintptr_t base, uint32_t wanted) {
    memset(d, 0, sizeof *d);
    d->base = base;
    if (mmio_read(base + 4) != 2)
        return false;
    mmio_write(base + 0x70, 0);
    barrier();
    mmio_write(base + 0x70, 1);
    mmio_write(base + 0x70, 3);
    mmio_write(base + 0x14, 0);
    d->features = mmio_read(base + 0x10) & wanted;
    mmio_write(base + 0x14, 1);
    if (!(mmio_read(base + 0x10) & 1))
        return false;
    mmio_write(base + 0x24, 0);
    mmio_write(base + 0x20, d->features);
    mmio_write(base + 0x24, 1);
    mmio_write(base + 0x20, 1); // VIRTIO_F_VERSION_1
    mmio_write(base + 0x70, 11);
    barrier();
    return (mmio_read(base + 0x70) & 8) != 0;
}
static void address(uintptr_t reg, uintptr_t value) {
    mmio_write(reg, (uint32_t)value);
    mmio_write(reg + 4, (uint32_t)(value >> 32));
}
bool virtio_queue(VDevice *d, unsigned n) {
    if (n > 1)
        return false;
    uintptr_t b = d->base;
    VQueue *q = &d->q[n];
    mmio_write(b + 0x30, n);
    if (mmio_read(b + 0x34) < VQ_SIZE)
        return false;
    q->number = n;
    q->avail.flags = 1; // Device completions are polled by a task.
    mmio_write(b + 0x38, VQ_SIZE);
    address(b + 0x80, (uintptr_t)q->desc);
    address(b + 0x90, (uintptr_t)&q->avail);
    address(b + 0xa0, (uintptr_t)&q->used);
    barrier();
    mmio_write(b + 0x44, 1);
    return true;
}
void virtio_ready(VDevice *d) {
    barrier();
    mmio_write(d->base + 0x70, 15);
}
void virtio_submit(VDevice *d, unsigned n, uint16_t head) {
    VQueue *q = &d->q[n];
    q->avail.ring[q->avail.idx % VQ_SIZE] = head;
    barrier();
    q->avail.idx++;
    barrier();
    mmio_write(d->base + 0x50, n);
}
