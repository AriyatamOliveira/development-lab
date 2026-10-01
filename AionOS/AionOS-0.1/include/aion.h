#ifndef AION_H
#define AION_H
#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
void *memset(void *, int, size_t);
void *memcpy(void *, const void *, size_t);
void *memmove(void *, const void *, size_t);
size_t strlen(const char *);
int strcmp(const char *, const char *);
void strcopy(char *, const char *, size_t);
void number(char *, uint64_t, unsigned);
void serial_putc(char);
void serial_write(const char *);
void serial_hex(uint64_t);
void serial_dec(uint64_t);
int serial_getc(void);
void boot_log(const char *);
__attribute__((noreturn)) void panic(const char *);
#define ASSERT(x)                                                                                  \
    do {                                                                                           \
        if (!(x))                                                                                  \
            panic("Assertion: " #x);                                                               \
    } while (0)
static inline void barrier(void) {
    __asm__ volatile("dsb sy" ::: "memory");
}
static inline uint32_t mmio_read(uintptr_t a) {
    return *(volatile uint32_t *)a;
}
static inline void mmio_write(uintptr_t a, uint32_t v) {
    *(volatile uint32_t *)a = v;
}
void memory_init(uintptr_t dtb);
void *page_alloc(void);
bool page_free(void *);
void *kmalloc(size_t);
void kfree(void *);
uint64_t memory_size(void);
void mmu_init(void);
void interrupts_init(void);
uint64_t ticks(void);
uint64_t millis(void);
void timer_init(void);
void sleep_ms(uint64_t);
__attribute__((noreturn)) void power_off(void);
__attribute__((noreturn)) void reboot(void);
void scheduler_init(void);
int task_create(const char *, void (*)(void *), void *);
void task_yield(void);
void scheduler_run(void);
void kernel_main(uintptr_t);
#endif
