#include "aion.h"
#include "graphics.h"
// This entry is linked only into build/exception.elf, never the normal OS.
void kernel_main(uintptr_t dtb) {
    boot_log("[TEST] Exception reporting test kernel");
    memory_init(dtb);
    mmu_init();
    interrupts_init();
    timer_init();
    ASSERT(graphics_init());
    boot_log("[TEST] Deliberate write outside the 32-bit virtual address space");
    uintptr_t unmapped = 0xffff000000000000UL;
    __asm__ volatile("str xzr, [%0]" ::"r"(unmapped) : "memory");
    panic("Abort did not occur");
}
