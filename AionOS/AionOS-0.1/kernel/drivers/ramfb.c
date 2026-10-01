#include "graphics.h"
#define FW 0x09020000UL
uint32_t framebuffer[SCREEN_W * SCREEN_H] __attribute__((aligned(4096)));
static uint16_t be16(uint16_t x) {
    return __builtin_bswap16(x);
}
static uint32_t be32(uint32_t x) {
    return __builtin_bswap32(x);
}
static uint64_t be64(uint64_t x) {
    return __builtin_bswap64(x);
}
static void select(uint16_t key) {
    *(volatile uint16_t *)(FW + 8) = be16(key);
    barrier();
}
static void read_bytes(void *dest, unsigned n) {
    uint8_t *d = dest;
    while (n--)
        *d++ = *(volatile uint8_t *)FW;
}
bool ramfb_init(void) {
    char sig[4];
    select(0);
    read_bytes(sig, 4);
    if (sig[0] != 'Q' || sig[1] != 'E')
        return false;
    select(0x19);
    uint32_t count;
    read_bytes(&count, 4);
    count = be32(count);
    if (count > 1024)
        return false;
    uint16_t key = 0;
    struct __attribute__((packed)) {
        uint32_t size;
        uint16_t select, reserved;
        char name[56];
    } file;
    for (unsigned i = 0; i < count; i++) {
        read_bytes(&file, sizeof file);
        file.name[55] = 0;
        if (!strcmp(file.name, "etc/ramfb"))
            key = be16(file.select);
    }
    if (!key)
        return false;
    struct __attribute__((packed)) {
        uint64_t addr;
        uint32_t fourcc, flags, w, h, stride;
    } cfg = {be64((uintptr_t)framebuffer),
             be32(0x34325258),
             0,
             be32(SCREEN_W),
             be32(SCREEN_H),
             be32(SCREEN_W * 4)};
    struct __attribute__((packed, aligned(16))) {
        volatile uint32_t control;
        uint32_t len;
        uint64_t addr;
    } dma = {be32((uint32_t)key << 16 | 8 | 16), be32(sizeof cfg), be64((uintptr_t)&cfg)};
    barrier();
    *(volatile uint64_t *)(FW + 16) = be64((uintptr_t)&dma);
    barrier();
    for (unsigned i = 0; i < 100000 && dma.control && !(be32(dma.control) & 1); i++)
        barrier();
    return dma.control == 0;
}
