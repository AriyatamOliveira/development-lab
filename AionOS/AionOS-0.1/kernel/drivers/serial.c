#include "aion.h"
#define UART 0x09000000UL
void serial_putc(char c) {
    if (c == '\n')
        serial_putc('\r');
    while (mmio_read(UART + 0x18) & (1 << 5)) {
    }
    mmio_write(UART, (uint32_t)c);
}
void serial_write(const char *s) {
    while (*s)
        serial_putc(*s++);
}
void serial_hex(uint64_t v) {
    char b[32];
    number(b, v, 16);
    serial_write("0x");
    serial_write(b);
}
void serial_dec(uint64_t v) {
    char b[32];
    number(b, v, 10);
    serial_write(b);
}
int serial_getc(void) {
    if (mmio_read(UART + 0x18) & (1 << 4))
        return -1;
    return mmio_read(UART) & 255;
}
