#include "fs.h"
#include "ui.h"
typedef struct Files {
    int dir, selected, scroll, action;
    int list[FS_NODES], count;
    uint64_t revision, last_click;
    int clicked;
} Files;
static void refresh(Window *w) {
    Files *f = w->state;
    if (!fs_node(f->dir)) {
        f->dir = 0;
        f->selected = -1;
    }
    f->count = fs_list(f->dir, f->list, FS_NODES);
    if (f->scroll > f->count - 8)
        f->scroll = f->count - 8;
    if (f->scroll < 0)
        f->scroll = 0;
    if (!fs_node(f->selected) || fs_node(f->selected)->parent != f->dir)
        f->selected = -1;
    f->revision = fs_revision();
}
static bool commit(void) {
    if (!fs_sync()) {
        ui_status("Changed in RAM; disk save failed. Retry before reboot.");
        return false;
    }
    ui_status(fs_persistent() ? "Saved to disk." : "Saved in RAM; files reset on shutdown.");
    return true;
}
static bool name_action(const char *name, void *ctx) {
    Window *w = ctx;
    if (!w->alive)
        return true;
    Files *f = w->state;
    if (f->action == 2) {
        if (!fs_rename(f->selected, name)) {
            ui_status(fs_error());
            return false;
        }
        serial_write("[FILES] Renamed: ");
        serial_write(name);
        serial_write("\n");
    } else {
        int id = fs_create(f->dir, name, f->action == 1);
        if (id < 0) {
            ui_status(fs_error());
            return false;
        }
        f->selected = id;
        serial_write(f->action == 1 ? "[FILES] Folder created: " : "[FILES] File created: ");
        serial_write(name);
        serial_write("\n");
    }
    commit();
    refresh(w);
    return true;
}
static bool delete_action(const char *ignored, void *ctx) {
    (void)ignored;
    Window *w = ctx;
    if (!w->alive)
        return true;
    Files *f = w->state;
    if (!fs_delete(f->selected)) {
        ui_status(fs_error());
        return true;
    }
    serial_write("[FILES] Entry deleted\n");
    f->selected = -1;
    commit();
    refresh(w);
    return true;
}
static void open_selected(Window *w) {
    Files *f = w->state;
    const FsNode *n = fs_node(f->selected);
    if (!n)
        return;
    if (n->dir) {
        f->dir = f->selected;
        f->selected = -1;
        f->scroll = 0;
        refresh(w);
    } else
        editor_open(f->selected);
    ui_dirty();
}
static void draw(Window *w) {
    Files *f = w->state;
    if (f->revision != fs_revision())
        refresh(w);
    ui_local_button(w, 12, 12, 72, "Back", false);
    ui_local_button(w, 96, 12, 110, "New File", true);
    ui_local_button(w, 218, 12, 120, "New Folder", false);
    ui_local_button(w, 350, 12, 96, "Rename", false);
    ui_local_button(w, 458, 12, 100, "Delete", false);
    char path[128];
    fs_path(f->dir, path, sizeof path);
    gfx_rect(w->x + 12, w->y + 88, w->w - 24, 24, C_DARK);
    gfx_text(w->x + 22, w->y + 95, path, C_MUTED, 1);
    ui_label(w, 22, 86, "Name", C_MUTED);
    ui_label(w, 438, 86, "Kind", C_MUTED);
    gfx_rect(w->x + 12, w->y + 136, w->w - 24, 208, C_DARK);
    for (int row = 0; row < 8 && f->scroll + row < f->count; row++) {
        int id = f->list[f->scroll + row];
        const FsNode *n = fs_node(id);
        int yy = 108 + row * 26;
        if (id == f->selected)
            gfx_rect(w->x + 14, w->y + 32 + yy, w->w - 28, 26, 0x2a4a63);
        gfx_text(w->x + 22, w->y + 32 + yy + 7, n->name, n->dir ? 0xd9b775 : C_LIGHT, 1);
        gfx_text(w->x + 438, w->y + 32 + yy + 7, n->dir ? "Folder" : "Text file", C_MUTED, 1);
    }
    ui_local_button(w, 12, 326, 100, "Open", true);
    ui_local_button(w, 126, 326, 72, "Up", false);
    ui_local_button(w, 210, 326, 80, "Down", false);
    char count[32], num[16];
    number(num, f->count, 10);
    strcopy(count, num, sizeof count);
    strcopy(count + strlen(count), " entries", sizeof(count) - strlen(count));
    ui_label(w, 330, 336, count, C_MUTED);
}
static void event(Window *w, InputEvent e) {
    Files *f = w->state;
    if (f->revision != fs_revision())
        refresh(w);
    if (e.type == INPUT_SCROLL) {
        f->scroll -= e.key;
        if (f->scroll < 0)
            f->scroll = 0;
        if (f->scroll > f->count - 8)
            f->scroll = f->count > 8 ? f->count - 8 : 0;
        return;
    }
    if (e.type == INPUT_KEY) {
        if (e.key == 10)
            open_selected(w);
        if (e.key == KEY_DELETE && f->selected >= 0)
            ui_confirm("Delete the selected entry?", delete_action, w);
        if (e.key == KEY_UP || e.key == KEY_DOWN) {
            int at = 0;
            for (int i = 0; i < f->count; i++)
                if (f->list[i] == f->selected)
                    at = i;
            if (e.key == KEY_DOWN && at + 1 < f->count)
                at++;
            if (e.key == KEY_UP && at > 0)
                at--;
            if (f->count)
                f->selected = f->list[at];
            if (at < f->scroll)
                f->scroll = at;
            if (at >= f->scroll + 8)
                f->scroll = at - 7;
        }
        return;
    }
    if (e.type != INPUT_BUTTON || !e.down)
        return;
    if (e.y >= 12 && e.y < 44) {
        if (e.x < 84) {
            if (f->dir)
                f->dir = fs_node(f->dir)->parent;
            f->selected = -1;
            f->scroll = 0;
            refresh(w);
        } else if (e.x >= 96 && e.x < 206) {
            f->action = 0;
            ui_prompt("Create a text file", "Untitled.txt", name_action, w);
        } else if (e.x >= 218 && e.x < 338) {
            f->action = 1;
            ui_prompt("Create a folder", "New Folder", name_action, w);
        } else if (e.x >= 350 && e.x < 446 && f->selected >= 0) {
            f->action = 2;
            ui_prompt("Rename selected entry", fs_node(f->selected)->name, name_action, w);
        } else if (e.x >= 458 && e.x < 558 && f->selected >= 0)
            ui_confirm("Delete the selected entry?", delete_action, w);
        return;
    }
    if (e.y >= 108 && e.y < 316) {
        int row = (e.y - 108) / 26 + f->scroll;
        if (row < f->count) {
            f->selected = f->list[row];
            uint64_t now = millis();
            if (f->clicked == f->selected && now - f->last_click < 400) {
                open_selected(w);
                f->clicked = -1;
            } else
                f->clicked = f->selected;
            f->last_click = now;
        }
        return;
    }
    if (e.y >= 326 && e.y < 358) {
        if (e.x < 112)
            open_selected(w);
        else if (e.x >= 126 && e.x < 198 && f->scroll > 0)
            f->scroll--;
        else if (e.x >= 210 && e.x < 290 && f->scroll + 8 < f->count)
            f->scroll++;
    }
}
void file_manager_open(void) {
    Window *w = ui_window("File Manager", 80, 110, 610, 420, sizeof(Files));
    if (!w)
        return;
    Files *f = w->state;
    f->dir = 0;
    f->selected = -1;
    f->clicked = -1;
    w->draw = draw;
    w->event = event;
    refresh(w);
    serial_write("[FILES] Window opened\n");
}
