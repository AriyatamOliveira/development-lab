#include "ui.h"
#define MAX_WINDOWS 6
static Window windows[MAX_WINDOWS];
Window *ui_order[MAX_WINDOWS];
int ui_count;
Window *ui_focus;
Window *ui_window(const char *title, int x, int y, int w, int h, size_t bytes) {
    if (ui_count == MAX_WINDOWS) {
        ui_status("Close a window first (maximum six).");
        return NULL;
    }
    Window *out = NULL;
    for (int i = 0; i < MAX_WINDOWS; i++)
        if (!windows[i].alive) {
            out = &windows[i];
            break;
        }
    ASSERT(out);
    memset(out, 0, sizeof *out);
    if (bytes) {
        out->state = kmalloc(bytes);
        if (!out->state) {
            ui_status("Out of application memory.");
            return NULL;
        }
        memset(out->state, 0, bytes);
    }
    out->alive = true;
    out->x = x;
    out->y = y;
    out->w = w;
    out->h = h;
    strcopy(out->title, title, sizeof out->title);
    ui_order[ui_count++] = out;
    ui_focus = out;
    ui_dirty();
    return out;
}
void ui_raise(Window *w) {
    for (int i = 0; i < ui_count; i++)
        if (ui_order[i] == w) {
            for (int j = i; j + 1 < ui_count; j++)
                ui_order[j] = ui_order[j + 1];
            ui_order[ui_count - 1] = w;
            break;
        }
    ui_focus = w;
    ui_dirty();
}
void ui_destroy(Window *w) {
    if (!w || !w->alive)
        return;
    for (int i = 0; i < ui_count; i++)
        if (ui_order[i] == w) {
            for (int j = i; j + 1 < ui_count; j++)
                ui_order[j] = ui_order[j + 1];
            ui_count--;
            break;
        }
    kfree(w->state);
    w->alive = false;
    ui_focus = ui_count ? ui_order[ui_count - 1] : NULL;
    ui_dirty();
}
void ui_draw_windows(void) {
    for (int i = 0; i < ui_count; i++) {
        Window *w = ui_order[i];
        gfx_rect(w->x + 6, w->y + 6, w->w, w->h, 0x080e18);
        gfx_rect(w->x, w->y, w->w, w->h, C_PANEL);
        gfx_rect(w->x, w->y, w->w, 32, w == ui_focus ? 0x30516b : 0x24394f);
        char shown[64];
        strcopy(shown, w->title, sizeof shown);
        int limit = (w->w - 60) / 12;
        if (limit < 63 && strlen(shown) > (size_t)limit) {
            shown[limit] = 0;
            shown[limit - 1] = '.';
            shown[limit - 2] = '.';
        }
        gfx_text(w->x + 12, w->y + 10, shown, C_LIGHT, 2);
        ui_button(w->x + w->w - 36, w->y + 2, 32, 28, "x", false);
        if (w->draw)
            w->draw(w);
    }
}
