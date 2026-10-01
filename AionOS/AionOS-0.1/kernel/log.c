#include "aion.h"
#include "graphics.h"
void boot_log(const char *s) {
    serial_write(s);
    serial_write("\n");
    gfx_boot(s);
}
void panic(const char *s) {
    __asm__ volatile("msr daifset, #0xf");
    serial_write("\nPANIC: ");
    serial_write(s);
    serial_write("\n");
    gfx_panic(s);
    for (;;)
        __asm__ volatile("wfe");
}
