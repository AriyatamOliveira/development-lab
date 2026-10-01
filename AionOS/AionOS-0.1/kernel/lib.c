#include "aion.h"
// Aligned word copies keep a full framebuffer update inexpensive even in TCG.
// The alias annotation allows these words to copy any object's representation.
typedef uint64_t CopyWord __attribute__((may_alias));
void *memset(void *p, int c, size_t n) {
    unsigned char *d = p;
    while (n && ((uintptr_t)d & 7)) {
        *d++ = (unsigned char)c;
        n--;
    }
    uint64_t word = (uint8_t)c;
    word |= word << 8;
    word |= word << 16;
    word |= word << 32;
    while (n >= 8) {
        *(CopyWord *)d = word;
        d += 8;
        n -= 8;
    }
    while (n--)
        *d++ = (unsigned char)c;
    return p;
}
void *memcpy(void *dest, const void *src, size_t n) {
    unsigned char *d = dest;
    const unsigned char *s = src;
    if (!(((uintptr_t)d | (uintptr_t)s) & 7)) {
        while (n >= 8) {
            *(CopyWord *)d = *(const CopyWord *)s;
            d += 8;
            s += 8;
            n -= 8;
        }
    }
    while (n--)
        *d++ = *s++;
    return dest;
}
void *memmove(void *d, const void *s, size_t n) {
    unsigned char *a = d;
    const unsigned char *b = s;
    if (a > b) {
        while (n) {
            n--;
            a[n] = b[n];
        }
    } else
        memcpy(d, s, n);
    return d;
}
size_t strlen(const char *s) {
    size_t n = 0;
    while (s[n])
        n++;
    return n;
}
int strcmp(const char *a, const char *b) {
    while (*a && *a == *b) {
        a++;
        b++;
    }
    return (unsigned char)*a - (unsigned char)*b;
}
void strcopy(char *d, const char *s, size_t cap) {
    if (!cap)
        return;
    size_t i = 0;
    while (i + 1 < cap && s[i]) {
        d[i] = s[i];
        i++;
    }
    d[i] = 0;
}
void number(char *out, uint64_t v, unsigned base) {
    char tmp[32];
    unsigned n = 0;
    do {
        tmp[n++] = "0123456789abcdef"[v % base];
        v /= base;
    } while (v);
    unsigned i = 0;
    while (n)
        out[i++] = tmp[--n];
    out[i] = 0;
}
