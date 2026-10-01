#include "aion.h"
static uint64_t level1[512] __attribute__((aligned(4096)));
void mmu_init(void) {
    // A 32-bit identity VA space starts at level 1 with 4 KiB granules.
    // Low 1 GiB is device memory and execute-never; RAM is normal uncached.
    // Cache-off normal RAM deliberately keeps DMA coherent for this first OS.
    level1[0] = (1UL << 54) | (1UL << 53) | (1UL << 10) | 1;
    level1[1] = 0x40000000UL | (1UL << 10) | (3UL << 8) | (1UL << 2) | 1;
    uint64_t mair = 0x4404, tcr = 32UL | (1UL << 23), sctlr;
    __asm__ volatile("msr mair_el1, %0; msr tcr_el1, %1; msr ttbr0_el1, %2; dsb sy; isb; tlbi "
                     "vmalle1; dsb sy; isb" ::"r"(mair),
                     "r"(tcr), "r"(level1)
                     : "memory");
    __asm__ volatile("mrs %0, sctlr_el1" : "=r"(sctlr));
    sctlr = (sctlr & ~((1UL << 2) | (1UL << 12))) | 1;
    __asm__ volatile("msr sctlr_el1, %0; isb" ::"r"(sctlr) : "memory");
}
