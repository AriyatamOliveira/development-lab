#ifndef VIRTIO_H
#define VIRTIO_H
#include "aion.h"
#define VQ_SIZE 64
struct VDesc {
    uint64_t addr;
    uint32_t len;
    uint16_t flags, next;
};
struct VAvail {
    volatile uint16_t flags, idx;
    uint16_t ring[VQ_SIZE];
    uint16_t event;
};
struct VUsedElem {
    uint32_t id, len;
};
struct VUsed {
    volatile uint16_t flags, idx;
    struct VUsedElem ring[VQ_SIZE];
    uint16_t event;
};
typedef struct VQueue {
    struct VDesc desc[VQ_SIZE] __attribute__((aligned(16)));
    struct VAvail avail __attribute__((aligned(2)));
    struct VUsed used __attribute__((aligned(4)));
    uint16_t seen, number;
} VQueue;
typedef struct VDevice {
    uintptr_t base;
    uint32_t features;
    VQueue q[2];
} VDevice;
bool virtio_init(VDevice *, uintptr_t, uint32_t);
bool virtio_queue(VDevice *, unsigned);
void virtio_ready(VDevice *);
void virtio_submit(VDevice *, unsigned, uint16_t);
void virtio_scan(void (*)(uintptr_t, unsigned));
bool block_init(void);
bool block_transfer(bool, uint64_t, void *, uint32_t);
bool block_flush(void);
bool block_ready(void);
uint64_t block_capacity(void);
#endif
