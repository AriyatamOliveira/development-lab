#include "fs.h"
#include "ui.h"
extern Window *ui_order[6], *ui_focus;
extern int ui_count;
extern void ui_draw_windows(void), ui_raise(Window *);
static bool dirty = true, logged_in = false;
static int mouse_x = 512, mouse_y = 384, menu;
static Window *drag;
static int drag_x, drag_y;
static char status[96];
static struct {
    bool active, confirm, selected;
    char title[80], text[128];
    PromptAction action;
    void *context;
} prompt;
void ui_dirty(void) {
    dirty = true;
}
void ui_status(const char *s) {
    strcopy(status, s, sizeof status);
    ui_dirty();
    serial_write("[UI] ");
    serial_write(s);
    serial_write("\n");
}
void ui_prompt(const char *title, const char *initial, PromptAction fn, void *ctx) {
    prompt.active = true;
    prompt.confirm = false;
    prompt.selected = true;
    strcopy(prompt.title, title, sizeof prompt.title);
    strcopy(prompt.text, initial, sizeof prompt.text);
    prompt.action = fn;
    prompt.context = ctx;
    ui_dirty();
}
void ui_confirm(const char *title, PromptAction fn, void *ctx) {
    ui_prompt(title, "", fn, ctx);
    prompt.confirm = true;
}
static void about_draw(Window *w) {
    ui_label(w, 22, 28, "AionOS 0.1", C_ACCENT);
    ui_label(w, 22, 70, "An original ARM64 learning OS.", C_LIGHT);
    ui_label(w, 22, 106, "Kernel tasks share one address space.", C_MUTED);
    ui_label(w, 22, 144, "Drag the title bar. Click x to close.", C_MUTED);
}
static void about_open(void) {
    Window *w = ui_window("About AionOS", 230, 210, 540, 240, 0);
    if (w)
        w->draw = about_draw;
}
static void clock_text(char *out) {
    uint32_t sec = mmio_read(0x09010000);
    unsigned h = (sec / 3600) % 24, m = (sec / 60) % 60;
    out[0] = '0' + h / 10;
    out[1] = '0' + h % 10;
    out[2] = ':';
    out[3] = '0' + m / 10;
    out[4] = '0' + m % 10;
    out[5] = 0;
}
static bool do_power(const char *unused, void *ctx) {
    (void)unused;
    if (!fs_sync()) {
        ui_status("Disk save failed. Retry before powering down.");
        return false;
    }
    if ((uintptr_t)ctx == 1)
        reboot();
    power_off();
}
static void draw(void) {
    for (int y = 0; y < SCREEN_H; y += 32)
        gfx_rect(0, y, SCREEN_W, 32, 0x101b30 + (uint32_t)(y / 64) * 0x010101);
    if (!logged_in) {
        gfx_rect(282, 160, 460, 420, C_PANEL);
        gfx_rect(474, 202, 76, 76, C_ACCENT);
        gfx_text(488, 214, "A", C_DARK, 8);
        gfx_text(386, 312, "AionOS", C_LIGHT, 7);
        gfx_text(362, 386, "A space to make things.", C_MUTED, 2);
        ui_button(362, 446, 300, 56, "Login", true);
        gfx_text(356, 538, "No password. Just get started.", C_MUTED, 2);
    } else {
        gfx_text(34, 32, "AionOS", C_ACCENT, 3);
        gfx_text(34, 64, "Your small ARM64 desktop", C_MUTED, 2);
        gfx_rect(34, 110, 52, 38, 0xd9b775);
        gfx_rect(34, 102, 25, 10, 0xd9b775);
        gfx_text(34, 164, "File Manager", C_LIGHT, 2);
        gfx_rect(34, 230, 42, 50, C_LIGHT);
        gfx_rect(43, 243, 24, 3, C_PANEL);
        gfx_rect(43, 253, 24, 3, C_PANEL);
        gfx_text(34, 296, "Text Editor", C_LIGHT, 2);
        ui_draw_windows();
        gfx_rect(0, 728, 1024, 40, C_DARK);
        ui_button(12, 732, 150, 32, "Applications", false);
        ui_button(174, 732, 100, 32, "Files", false);
        ui_button(286, 732, 110, 32, "Editor", false);
        char c[6];
        clock_text(c);
        gfx_text(686, 742, c, C_LIGHT, 2);
        gfx_text(754, 742, "UTC", C_MUTED, 1);
        ui_button(834, 732, 174, 32, "Power", false);
        if (menu == 1) {
            gfx_rect(12, 560, 236, 156, C_PANEL);
            ui_button(22, 570, 216, 38, "File Manager", false);
            ui_button(22, 616, 216, 38, "Text Editor", false);
            ui_button(22, 662, 216, 38, "About AionOS", false);
        }
        if (menu == 2) {
            gfx_rect(798, 612, 210, 104, C_PANEL);
            ui_button(808, 622, 190, 36, "Reboot", false);
            ui_button(808, 668, 190, 36, "Shutdown", false);
        }
        if (status[0]) {
            gfx_rect(210, 696, 800, 26, C_DARK);
            gfx_text(220, 702, status, C_MUTED, 1);
        }
    }
    if (prompt.active) {
        gfx_rect(240, 284, 544, 194, 0x08111d);
        gfx_rect(234, 278, 544, 194, 0x2a4160);
        gfx_text(256, 302, prompt.title, C_LIGHT, 2);
        if (!prompt.confirm) {
            gfx_rect(256, 340, 500, 36, C_DARK);
            if (prompt.selected)
                gfx_rect(264, 346, 492, 24, 0x30516b);
            const char *shown = prompt.text;
            size_t plen = strlen(shown);
            if (plen > 40)
                shown += plen - 40;
            gfx_text(266, 350, shown, C_LIGHT, 2);
            int caret = (int)strlen(prompt.text);
            if (caret > 40)
                caret = 40;
            gfx_rect(266 + caret * 12, 350, 2, 14, C_ACCENT);
        }
        ui_button(462, 410, 130, 38, "Cancel", false);
        ui_button(608, 410, 148, 38, prompt.confirm ? "Confirm" : "OK", true);
    }
    gfx_cursor(mouse_x, mouse_y);
    gfx_present();
    dirty = false;
}
static void accept_prompt(void) {
    PromptAction fn = prompt.action;
    void *ctx = prompt.context;
    prompt.active = false;
    if (fn && !fn(prompt.text, ctx))
        prompt.active = true;
    ui_dirty();
}
static void dispatch(InputEvent e) {
    if (e.type == INPUT_POINTER) {
        mouse_x = e.x;
        mouse_y = e.y;
        if (drag) {
            drag->x = e.x - drag_x;
            drag->y = e.y - drag_y;
            if (drag->x < 0)
                drag->x = 0;
            if (drag->x > SCREEN_W - drag->w)
                drag->x = SCREEN_W - drag->w;
            if (drag->y < 0)
                drag->y = 0;
            if (drag->y > 696 - drag->h)
                drag->y = 696 - drag->h;
        }
        ui_dirty();
        return;
    }
    if (e.type == INPUT_BUTTON && !e.down) {
        drag = NULL;
        return;
    }
    if (prompt.active) {
        if (e.type == INPUT_KEY) {
            size_t n = strlen(prompt.text);
            if (e.key == KEY_ESC) {
                prompt.active = false;
            } else if (e.key == 10)
                accept_prompt();
            else if (e.ctrl && (e.key == 'a' || e.key == 'A'))
                prompt.selected = true;
            else if (!prompt.confirm && e.key == 8) {
                if (prompt.selected)
                    prompt.text[0] = 0;
                else if (n)
                    prompt.text[n - 1] = 0;
                prompt.selected = false;
            } else if (!prompt.confirm && e.key >= 32 && e.key < 127) {
                if (prompt.selected) {
                    prompt.text[0] = 0;
                    n = 0;
                    prompt.selected = false;
                }
                if (n + 1 < sizeof prompt.text) {
                    prompt.text[n] = e.key;
                    prompt.text[n + 1] = 0;
                }
            }
            ui_dirty();
        }
        if (e.type == INPUT_BUTTON && e.down) {
            if (ui_inside(e.x, e.y, 462, 410, 130, 38))
                prompt.active = false;
            else if (ui_inside(e.x, e.y, 608, 410, 148, 38))
                accept_prompt();
            ui_dirty();
        }
        return;
    }
    if (!logged_in) {
        if ((e.type == INPUT_BUTTON && e.down && ui_inside(e.x, e.y, 362, 446, 300, 56)) ||
            (e.type == INPUT_KEY && e.key == 10)) {
            logged_in = true;
            serial_write("[UI] Desktop entered\n");
            ui_dirty();
        }
        return;
    }
    if (e.type == INPUT_BUTTON && e.down) {
        if (e.y >= 728) {
            if (e.x < 162)
                menu = menu == 1 ? 0 : 1;
            else if (e.x < 274) {
                menu = 0;
                file_manager_open();
            } else if (e.x < 396) {
                menu = 0;
                editor_open(-1);
            } else if (e.x >= 834)
                menu = menu == 2 ? 0 : 2;
            ui_dirty();
            return;
        }
        if (menu == 1 && ui_inside(e.x, e.y, 12, 560, 236, 156)) {
            int action = (e.y - 570) / 46;
            menu = 0;
            if (action == 0)
                file_manager_open();
            else if (action == 1)
                editor_open(-1);
            else
                about_open();
            ui_dirty();
            return;
        }
        if (menu == 2 && ui_inside(e.x, e.y, 798, 612, 210, 104)) {
            menu = 0;
            uintptr_t action = e.y < 662 ? 1 : 2;
            if (editor_has_unsaved())
                ui_confirm("Discard unsaved text and power down?", do_power, (void *)action);
            else
                do_power("", (void *)action);
            return;
        }
        menu = 0;
        for (int i = ui_count - 1; i >= 0; i--) {
            Window *w = ui_order[i];
            if (ui_inside(e.x, e.y, w->x, w->y, w->w, w->h)) {
                ui_raise(w);
                if (e.y < w->y + 32) {
                    if (e.x > w->x + w->w - 38) {
                        if (!w->close || w->close(w))
                            ui_destroy(w);
                    } else {
                        drag = w;
                        drag_x = e.x - w->x;
                        drag_y = e.y - w->y;
                    }
                    return;
                }
                e.x -= w->x;
                e.y -= w->y + 32;
                if (w->event)
                    w->event(w, e);
                ui_dirty();
                return;
            }
        }
        if (ui_inside(e.x, e.y, 26, 96, 160, 94))
            file_manager_open();
        else if (ui_inside(e.x, e.y, 26, 218, 160, 98))
            editor_open(-1);
        ui_dirty();
        return;
    }
    if ((e.type == INPUT_KEY || e.type == INPUT_SCROLL) && ui_focus && ui_focus->event) {
        ui_focus->event(ui_focus, e);
        ui_dirty();
    }
}
void ui_init(void) {
    dirty = true;
    logged_in = false;
    serial_write("[UI] Login ready\n");
}
void ui_task(void *arg) {
    (void)arg;
    uint64_t last = 0;
    for (;;) {
        InputEvent e;
        while (input_next(&e))
            dispatch(e);
        uint64_t now = millis() / 1000;
        if (now != last) {
            last = now;
            dirty = true;
        }
        if (dirty)
            draw();
        task_yield();
    }
}
void input_task(void *arg) {
    (void)arg;
    for (;;) {
        input_poll();
        task_yield();
        __asm__ volatile("wfi");
    }
}
