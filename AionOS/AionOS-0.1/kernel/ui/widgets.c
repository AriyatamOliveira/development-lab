#include "ui.h"
bool ui_inside(int x, int y, int left, int top, int w, int h) {
    return x >= left && y >= top && x < left + w && y < top + h;
}
void ui_button(int x, int y, int w, int h, const char *s, bool accent) {
    gfx_rect(x, y, w, h, accent ? C_ACCENT : 0x2a4160);
    int scale = (int)strlen(s) * 12 > w - 24 ? 1 : 2;
    gfx_text(x + 12, y + (h - 7 * scale) / 2, s, accent ? C_DARK : C_LIGHT, scale);
}
void ui_label(Window *w, int x, int y, const char *s, uint32_t c) {
    gfx_text(w->x + x, w->y + 32 + y, s, c, 2);
}
void ui_local_button(Window *w, int x, int y, int width, const char *s, bool accent) {
    ui_button(w->x + x, w->y + 32 + y, width, 32, s, accent);
}
