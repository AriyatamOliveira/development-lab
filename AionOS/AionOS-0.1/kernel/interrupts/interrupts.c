#include "aion.h"
#include "graphics.h"
#define GICD 0x08000000UL
#define GICC 0x08010000UL
extern char exception_vectors[];
static volatile uint64_t tick_count;
static uint64_t frequency;
void interrupts_init(void) {
    __asm__ volatile("msr vbar_el1, %0; isb" ::"r"(exception_vectors) : "memory");
    // GICv2: IRQ 27 is the per-CPU ARM virtual timer. Group 0, single CPU.
    mmio_write(GICD, 1);
    mmio_write(GICD + 0x100, 1u << 27);
    *(volatile uint8_t *)(GICD + 0x400 + 27) = 0x80;
    mmio_write(GICC + 4, 0xff);
    mmio_write(GICC, 1);
    barrier();
}
void timer_init(void) {
    __asm__ volatile("mrs %0, cntfrq_el0" : "=r"(frequency));
    uint64_t interval = frequency / 100;
    __asm__ volatile(
        "msr cntv_tval_el0, %0; msr cntv_ctl_el0, %1; isb; msr daifclr, #2" ::"r"(interval),
        "r"((uint64_t)1)
        : "memory");
}
void irq_dispatch(uint64_t *frame) {
    (void)frame;
    uint32_t irq = mmio_read(GICC + 0x0c);
    if ((irq & 1023) == 27) {
        tick_count++;
        uint64_t interval = frequency / 100;
        __asm__ volatile("msr cntv_tval_el0, %0; isb" ::"r"(interval));
    }
    if ((irq & 1023) < 1020)
        mmio_write(GICC + 0x10, irq);
}
uint64_t ticks(void) {
    return tick_count;
}
uint64_t millis(void) {
    uint64_t c;
    __asm__ volatile("mrs %0, cntvct_el0" : "=r"(c));
    return frequency ? c / (frequency / 1000) : 0;
}
void sleep_ms(uint64_t n) {
    uint64_t end = millis() + n;
    while (millis() < end)
        __asm__ volatile("wfi");
}
void exception_fatal(uint64_t *f) {
    uint64_t esr, far;
    __asm__ volatile("mrs %0, esr_el1; mrs %1, far_el1" : "=r"(esr), "=r"(far));
    serial_write("\nPANIC: ");
    unsigned ec = esr >> 26;
    const char *reason = ec == 0x25 || ec == 0x24 ? "Data Abort"
                         : ec == 0x3c             ? "Breakpoint"
                                                  : "CPU exception";
    serial_write(reason);
    serial_write("\nPC: ");
    serial_hex(f[31]);
    serial_write("\nSP: ");
    serial_hex((uintptr_t)f + 272);
    serial_write("\nESR_EL1: ");
    serial_hex(esr);
    serial_write("\nFAR_EL1: ");
    serial_hex(far);
    serial_write("\nSPSR_EL1: ");
    serial_hex(f[32]);
    for (unsigned i = 0; i < 31; i++) {
        serial_write("\nx");
        serial_dec(i);
        serial_write(": ");
        serial_hex(f[i]);
    }
    __asm__ volatile("msr daifset, #0xf");
    gfx_exception(reason, f[31], (uintptr_t)f + 272, esr, far);
    serial_write("\n[HALT] Fatal exception; CPU halted\n");
    for (;;)
        __asm__ volatile("wfe");
}
