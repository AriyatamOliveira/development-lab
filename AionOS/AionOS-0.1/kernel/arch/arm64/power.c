#include "aion.h"
static __attribute__((noreturn)) void psci(uint64_t fn) {
    register uint64_t x0 __asm__("x0") = fn;
    __asm__ volatile("hvc #0" : "+r"(x0)::"x1", "x2", "x3", "memory");
    panic("PSCI power request returned unexpectedly");
}
void power_off(void) {
    boot_log("[POWER] Shutdown");
    psci(0x84000008);
}
void reboot(void) {
    boot_log("[POWER] Reboot");
    psci(0x84000009);
}
