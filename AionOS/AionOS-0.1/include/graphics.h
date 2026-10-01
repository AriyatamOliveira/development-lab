#ifndef GRAPHICS_H
#define GRAPHICS_H
#include "aion.h"
#define SCREEN_W 1024
#define SCREEN_H 768
#define C_BG 0x101c30
#define C_PANEL 0x1a2c46
#define C_LIGHT 0xf1f5fb
#define C_MUTED 0x98abc5
#define C_ACCENT 0x60dbbd
#define C_DARK 0x0b1424
bool graphics_init(void);
bool graphics_ready(void);
void gfx_rect(int, int, int, int, uint32_t);
void gfx_text(int, int, const char *, uint32_t, int);
void gfx_char(int, int, char, uint32_t, int);
void gfx_present(void);
void gfx_cursor(int, int);
void gfx_boot(const char *);
void gfx_panic(const char *);
void gfx_exception(const char *, uint64_t, uint64_t, uint64_t, uint64_t);
#endif
