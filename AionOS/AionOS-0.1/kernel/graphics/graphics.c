#include "graphics.h"
extern uint32_t framebuffer[];
extern bool ramfb_init(void);
static uint32_t back[SCREEN_W * SCREEN_H] __attribute__((aligned(4096)));
static bool ready;
static int boot_y = 114;
bool graphics_init(void) {
    ready = ramfb_init();
    return ready;
}
bool graphics_ready(void) {
    return ready;
}
void gfx_rect(int x, int y, int w, int h, uint32_t c) {
    if (x < 0) {
        w += x;
        x = 0;
    }
    if (y < 0) {
        h += y;
        y = 0;
    }
    if (x + w > SCREEN_W)
        w = SCREEN_W - x;
    if (y + h > SCREEN_H)
        h = SCREEN_H - y;
    for (int row = 0; row < h; row++)
        for (int col = 0; col < w; col++)
            back[(y + row) * SCREEN_W + x + col] = c;
}
void gfx_present(void) {
    if (ready) {
        memcpy(framebuffer, back, sizeof back);
        barrier();
    }
}
void gfx_cursor(int x, int y) {
    for (int row = 0; row < 19; row++)
        for (int col = 0; col <= row / 2; col++)
            gfx_rect(x + col, y + row, 1, 1,
                     col == 0 || col == row / 2 || row == 18 ? C_DARK : C_LIGHT);
}
void gfx_boot(const char *s) {
    if (!ready)
        return;
    if (boot_y == 114) {
        gfx_rect(0, 0, SCREEN_W, SCREEN_H, C_BG);
        gfx_text(40, 40, "AionOS", C_ACCENT, 5);
        gfx_text(42, 88, "ARM64 / native kernel / boot diagnostics", C_MUTED, 2);
    }
    gfx_text(42, boot_y, s, C_LIGHT, 2);
    boot_y += 24;
    gfx_present();
}
void gfx_panic(const char *s) {
    if (!ready)
        return;
    gfx_rect(30, 30, SCREEN_W - 60, SCREEN_H - 60, 0x401826);
    gfx_text(60, 60, "KERNEL PANIC", 0xffadb9, 3);
    gfx_text(60, 110, s, C_LIGHT, 2);
    gfx_text(60, 170, "Register details are on the serial console.", C_MUTED, 2);
    gfx_present();
}

void gfx_exception(const char *reason, uint64_t pc, uint64_t sp, uint64_t esr, uint64_t far) {
    if (!ready)
        return;
    gfx_panic(reason);
    const char *labels[] = {"PC:", "SP:", "ESR_EL1:", "FAR_EL1:"};
    uint64_t values[] = {pc, sp, esr, far};
    gfx_rect(60, 160, SCREEN_W - 120, 240, 0x401826);
    for (int i = 0; i < 4; i++) {
        char text[32];
        number(text, values[i], 16);
        gfx_text(60, 172 + i * 40, labels[i], C_MUTED, 2);
        gfx_text(230, 172 + i * 40, "0x", C_LIGHT, 2);
        gfx_text(254, 172 + i * 40, text, C_LIGHT, 2);
    }
    gfx_text(60, 374, "CPU halted. Full register dump: serial console.", C_MUTED, 2);
    gfx_present();
}
