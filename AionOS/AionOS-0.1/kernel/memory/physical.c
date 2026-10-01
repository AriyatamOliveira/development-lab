#include "aion.h"
extern char __kernel_end[];
static uintptr_t first;
static uint64_t ram_bytes = 256UL * 1024 * 1024;
static uint8_t allocated[65536 / 8];
static unsigned count;
static uint32_t be32(const void *p) {
    const uint8_t *b = p;
    return (uint32_t)b[0] << 24 | (uint32_t)b[1] << 16 | (uint32_t)b[2] << 8 | b[3];
}
static uint64_t be64(const void *p) {
    return (uint64_t)be32(p) << 32 | be32((const uint8_t *)p + 4);
}
// Minimal FDT reader: find a memory node's reg property. The prescribed
// QEMU virt machine uses two address cells and two size cells.
static void read_memory(uintptr_t addr) {
    if (addr < 0x40000000 || addr >= 0x50000000)
        return;
    const uint8_t *b = (const uint8_t *)addr;
    if (be32(b) != 0xd00dfeed)
        return;
    uint32_t total = be32(b + 4), so = be32(b + 8), ss = be32(b + 12);
    if (total > 2 * 1024 * 1024 || so >= total || ss >= total)
        return;
    const uint8_t *p = b + so, *end = b + total;
    bool in_memory = false;
    while (p + 4 <= end) {
        unsigned tag = be32(p);
        p += 4;
        if (tag == 1) {
            const char *name = (const char *)p;
            size_t n = 0;
            while (p + n < end && p[n])
                n++;
            if (p + n >= end)
                return;
            in_memory = n >= 6 && name[0] == 'm' && name[1] == 'e' && name[2] == 'm' &&
                        name[3] == 'o' && name[4] == 'r' && name[5] == 'y';
            p += (n + 4) & ~3UL;
        } else if (tag == 2)
            in_memory = false;
        else if (tag == 3) {
            if (p + 8 > end)
                return;
            unsigned n = be32(p), o = be32(p + 4);
            p += 8;
            if (p + n > end || ss + o + 4 > total)
                return;
            if (in_memory && strcmp((const char *)b + ss + o, "reg") == 0 && n >= 16 &&
                be64(p) == 0x40000000) {
                ram_bytes = be64(p + 8);
                return;
            }
            p += (n + 3) & ~3UL;
        } else if (tag == 9)
            return;
        else if (tag != 4)
            return;
    }
}
void memory_init(uintptr_t dtb) {
    read_memory(dtb);
    if (!dtb)
        read_memory(0x40000000);
    // The bitmap supports the project's fixed 256 MiB target only.
    if (ram_bytes > 256UL * 1024 * 1024)
        ram_bytes = 256UL * 1024 * 1024;
    first = ((uintptr_t)__kernel_end + 4095) & ~4095UL;
    ASSERT(first < 0x40000000 + ram_bytes);
    count = (0x40000000 + ram_bytes - first) / 4096;
    memset(allocated, 0, sizeof allocated);
}
uint64_t memory_size(void) {
    return ram_bytes;
}
void *page_alloc(void) {
    for (unsigned i = 0; i < count; i++)
        if (!(allocated[i / 8] & (1u << (i % 8)))) {
            allocated[i / 8] |= 1u << (i % 8);
            void *p = (void *)(first + i * 4096UL);
            memset(p, 0, 4096);
            return p;
        }
    return NULL;
}
bool page_free(void *p) {
    uintptr_t a = (uintptr_t)p;
    if (a < first || (a - first) % 4096)
        return false;
    unsigned i = (a - first) / 4096;
    if (i >= count || !(allocated[i / 8] & (1u << (i % 8))))
        return false;
    allocated[i / 8] &= ~(1u << (i % 8));
    return true;
}
