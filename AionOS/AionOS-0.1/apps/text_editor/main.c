#include "fs.h"
#include "ui.h"
#define COLS 54
#define ROWS 17
#define CELL_H 18
typedef struct Editor {
    char text[FS_DATA];
    int file, overwrite;
    uint32_t identity, saved_hash;
    size_t length, cursor;
    int scroll;
    bool modified, selected;
} Editor;
static uint32_t hash(const char *s, size_t n) {
    uint32_t h = 2166136261u;
    for (size_t i = 0; i < n; i++)
        h = (h ^ (uint8_t)s[i]) * 16777619u;
    return h;
}
static void title(Window *w) {
    Editor *e = w->state;
    const FsNode *n = fs_node(e->file);
    strcopy(w->title, e->modified ? "* " : "", sizeof w->title);
    size_t used = strlen(w->title);
    strcopy(w->title + used, n && n->identity == e->identity ? n->name : "Untitled",
            sizeof(w->title) - used);
}
static void position(Editor *e, size_t pos, int *row, int *col) {
    *row = 0;
    *col = 0;
    for (size_t i = 0; i < pos && i < e->length; i++) {
        if (e->text[i] == '\n') {
            (*row)++;
            *col = 0;
        } else if (++*col == COLS) {
            (*row)++;
            *col = 0;
        }
    }
}
static size_t index_at(Editor *e, int target, int column) {
    if (target < 0)
        return 0;
    int row = 0, col = 0;
    for (size_t i = 0; i < e->length; i++) {
        if (row == target && (col >= column || e->text[i] == '\n'))
            return i;
        if (row > target)
            return i;
        if (e->text[i] == '\n') {
            row++;
            col = 0;
        } else if (++col == COLS) {
            row++;
            col = 0;
        }
    }
    return e->length;
}
static void ensure_cursor(Editor *e) {
    int row, col;
    position(e, e->cursor, &row, &col);
    if (row < e->scroll)
        e->scroll = row;
    if (row >= e->scroll + ROWS)
        e->scroll = row - ROWS + 1;
    if (e->scroll < 0)
        e->scroll = 0;
}
static bool finish_save(Window *w, int id) {
    Editor *e = w->state;
    if (!fs_write(id, e->text, e->length)) {
        ui_status(fs_error());
        return false;
    }
    const FsNode *n = fs_node(id);
    e->file = id;
    e->identity = n->identity;
    e->saved_hash = hash(n->data, n->size);
    if (!fs_sync()) {
        e->modified = true;
        title(w);
        ui_status("Disk save failed. Text is in RAM; retry Save.");
        return false;
    }
    e->modified = false;
    title(w);
    ui_status(fs_persistent() ? "Text saved to disk."
                              : "Text saved in RAM; it resets on shutdown.");
    serial_write("[EDITOR] Saved: ");
    serial_write(n->name);
    serial_write("\n");
    return true;
}
static bool overwrite_action(const char *unused, void *ctx) {
    (void)unused;
    Window *w = ctx;
    if (!w->alive)
        return true;
    Editor *e = w->state;
    finish_save(w, e->overwrite);
    return true;
}
static bool save_as_action(const char *path, void *ctx) {
    Window *w = ctx;
    if (!w->alive)
        return true;
    Editor *e = w->state;
    char name[FS_NAME], parent[128];
    const char *last = NULL;
    for (const char *p = path; *p; p++)
        if (*p == '/')
            last = p;
    int dir = fs_lookup("/Documents");
    if (last) {
        size_t n = last - path;
        if (path[0] != '/' || n >= sizeof parent) {
            ui_status("Use an absolute path or a filename.");
            return false;
        }
        memcpy(parent, path, n);
        parent[n] = 0;
        dir = n ? fs_lookup(parent) : 0;
        path = last + 1;
    }
    if (strlen(path) >= sizeof name) {
        ui_status("Filename is too long.");
        return false;
    }
    strcopy(name, path, sizeof name);
    int id = fs_find(dir, name);
    if (id >= 0) {
        if (fs_node(id)->dir) {
            ui_status("That path is a folder.");
            return false;
        }
        if (id == e->file && fs_node(id)->identity == e->identity)
            return finish_save(w, id);
        e->overwrite = id;
        ui_confirm("Replace the existing text file?", overwrite_action, w);
        return true;
    }
    id = fs_create(dir, name, false);
    if (id < 0) {
        ui_status(fs_error());
        return false;
    }
    return finish_save(w, id);
}
static void save_as(Window *w) {
    Editor *e = w->state;
    char path[128];
    const FsNode *n = fs_node(e->file);
    if (n && n->identity == e->identity)
        fs_path(e->file, path, sizeof path);
    else
        strcopy(path, "/Documents/Untitled.txt", sizeof path);
    ui_prompt("Save As: full path or filename", path, save_as_action, w);
}
static void save(Window *w) {
    Editor *e = w->state;
    const FsNode *n = fs_node(e->file);
    if (!n || n->identity != e->identity) {
        save_as(w);
        return;
    }
    if (hash(n->data, n->size) != e->saved_hash) {
        ui_status("File changed in another editor. Use Save As.");
        return;
    }
    finish_save(w, e->file);
}
static bool open_action(const char *path, void *ctx) {
    (void)ctx;
    int id = fs_lookup(path);
    const FsNode *n = fs_node(id);
    if (!n || n->dir) {
        ui_status("Enter the full path of a text file.");
        return false;
    }
    editor_open(id);
    return true;
}
static bool discard_action(const char *unused, void *ctx) {
    (void)unused;
    ui_destroy(ctx);
    return true;
}
static bool close_editor(Window *w) {
    Editor *e = w->state;
    if (!e->modified)
        return true;
    ui_confirm("Discard unsaved changes and close?", discard_action, w);
    return false;
}
static void draw(Window *w) {
    Editor *e = w->state;
    title(w);
    ui_local_button(w, 12, 12, 72, "New", false);
    ui_local_button(w, 96, 12, 72, "Open", false);
    ui_local_button(w, 180, 12, 84, "Save", true);
    ui_local_button(w, 276, 12, 108, "Save As", false);
    ui_local_button(w, 420, 12, 84, "Up", false);
    ui_local_button(w, 516, 12, 84, "Down", false);
    char path[128];
    const FsNode *n = fs_node(e->file);
    if (n && n->identity == e->identity)
        fs_path(e->file, path, sizeof path);
    else
        strcopy(path, "Unsaved document", sizeof path);
    gfx_text(w->x + 24, w->y + 92, path, C_MUTED, 1);
    gfx_rect(w->x + 12, w->y + 116, w->w - 24, ROWS * CELL_H + 20, C_DARK);
    if (e->selected)
        gfx_rect(w->x + 20, w->y + 124, COLS * 12, ROWS * CELL_H, 0x25455b);
    int row = 0, col = 0;
    for (size_t i = 0; i < e->length; i++) {
        char c = e->text[i];
        if (c == '\n') {
            row++;
            col = 0;
            continue;
        }
        if (row >= e->scroll && row < e->scroll + ROWS)
            gfx_char(w->x + 24 + col * 12, w->y + 128 + (row - e->scroll) * CELL_H, c, C_LIGHT, 2);
        if (++col == COLS) {
            row++;
            col = 0;
        }
    }
    position(e, e->cursor, &row, &col);
    if (row >= e->scroll && row < e->scroll + ROWS)
        gfx_rect(w->x + 24 + col * 12, w->y + 128 + (row - e->scroll) * CELL_H, 2, 14, C_ACCENT);
    char summary[96], num[20];
    strcopy(summary, e->modified ? "Modified | " : "Saved | ", sizeof summary);
    number(num, e->length, 10);
    strcopy(summary + strlen(summary), num, sizeof(summary) - strlen(summary));
    strcopy(summary + strlen(summary), " / 4095 bytes | Ctrl+S to save",
            sizeof(summary) - strlen(summary));
    gfx_text(w->x + 24, w->y + w->h - 22, summary, C_MUTED, 1);
}
static void edit_key(Window *w, InputEvent ev) {
    Editor *e = w->state;
    int key = ev.key;
    if (ev.ctrl) {
        if (key == 's' || key == 'S') {
            if (ev.shift)
                save_as(w);
            else
                save(w);
        } else if (key == 'n' || key == 'N')
            editor_open(-1);
        else if (key == 'o' || key == 'O')
            ui_prompt("Open: full path", "/Documents/Welcome.txt", open_action, w);
        else if (key == 'a' || key == 'A')
            e->selected = true;
        return;
    }
    bool changed = false;
    int row, col;
    position(e, e->cursor, &row, &col);
    if ((key == 8 || key == KEY_DELETE || key == 10 || key == 9 || (key >= 32 && key < 127)) &&
        e->selected) {
        e->text[0] = 0;
        e->length = e->cursor = 0;
        e->scroll = 0;
        e->selected = false;
        changed = true;
        if (key == 8 || key == KEY_DELETE) {
            e->modified = true;
            title(w);
            return;
        }
    }
    if (key == KEY_LEFT) {
        if (e->cursor)
            e->cursor--;
        e->selected = false;
    } else if (key == KEY_RIGHT) {
        if (e->cursor < e->length)
            e->cursor++;
        e->selected = false;
    } else if (key == KEY_UP || key == KEY_DOWN) {
        e->cursor = index_at(e, row + (key == KEY_UP ? -1 : 1), col);
        e->selected = false;
    } else if (key == KEY_HOME) {
        e->cursor = index_at(e, row, 0);
        e->selected = false;
    } else if (key == KEY_END) {
        e->cursor = index_at(e, row, COLS);
        e->selected = false;
    } else if (key == KEY_PAGEUP || key == KEY_PAGEDOWN) {
        e->cursor = index_at(e, row + (key == KEY_PAGEUP ? -ROWS : ROWS), col);
        e->selected = false;
    } else if (key == 8 && e->cursor) {
        memmove(e->text + e->cursor - 1, e->text + e->cursor, e->length - e->cursor + 1);
        e->cursor--;
        e->length--;
        changed = true;
    } else if (key == KEY_DELETE && e->cursor < e->length) {
        memmove(e->text + e->cursor, e->text + e->cursor + 1, e->length - e->cursor);
        e->length--;
        changed = true;
    } else if (key == 10 || key == 9 || (key >= 32 && key < 127)) {
        unsigned add = key == 9 ? 4 : 1;
        if (e->length + add >= FS_DATA) {
            ui_status("Document full (4095 bytes maximum).");
            return;
        }
        memmove(e->text + e->cursor + add, e->text + e->cursor, e->length - e->cursor + 1);
        for (unsigned i = 0; i < add; i++)
            e->text[e->cursor + i] = key == 9 ? ' ' : key;
        e->cursor += add;
        e->length += add;
        changed = true;
    }
    if (changed)
        e->modified = true;
    ensure_cursor(e);
    title(w);
}
static void event(Window *w, InputEvent ev) {
    Editor *e = w->state;
    if (ev.type == INPUT_KEY) {
        edit_key(w, ev);
        return;
    }
    if (ev.type == INPUT_SCROLL) {
        e->scroll -= ev.key;
        int rows, col;
        position(e, e->length, &rows, &col);
        int max = rows >= ROWS ? rows - ROWS + 1 : 0;
        if (e->scroll < 0)
            e->scroll = 0;
        if (e->scroll > max)
            e->scroll = max;
        return;
    }
    if (ev.type != INPUT_BUTTON || !ev.down)
        return;
    if (ev.y >= 12 && ev.y < 44) {
        if (ev.x < 84)
            editor_open(-1);
        else if (ev.x >= 96 && ev.x < 168)
            ui_prompt("Open: full path", "/Documents/Welcome.txt", open_action, w);
        else if (ev.x >= 180 && ev.x < 264)
            save(w);
        else if (ev.x >= 276 && ev.x < 384)
            save_as(w);
        else if (ev.x >= 420 && ev.x < 504) {
            if (e->scroll > 0)
                e->scroll--;
        } else if (ev.x >= 516 && ev.x < 600) {
            int rows, col;
            position(e, e->length, &rows, &col);
            if (e->scroll + ROWS <= rows)
                e->scroll++;
        }
        return;
    }
    if (ev.y >= 96 && ev.y < 96 + ROWS * CELL_H) {
        int col = (ev.x - 24) / 12;
        if (col < 0)
            col = 0;
        if (col > COLS)
            col = COLS;
        e->cursor = index_at(e, e->scroll + (ev.y - 96) / CELL_H, col);
        e->selected = false;
        ensure_cursor(e);
    }
}
void editor_open(int id) {
    const FsNode *n = fs_node(id);
    if (id >= 0 && (!n || n->dir)) {
        ui_status("Choose a text file.");
        return;
    }
    Window *w = ui_window("Text Editor", 260, 164, 700, 476, sizeof(Editor));
    if (!w)
        return;
    Editor *e = w->state;
    e->file = -1;
    if (n) {
        e->file = id;
        e->identity = n->identity;
        e->length = n->size;
        memcpy(e->text, n->data, n->size + 1);
        e->saved_hash = hash(n->data, n->size);
    }
    w->draw = draw;
    w->event = event;
    w->close = close_editor;
    title(w);
    serial_write("[EDITOR] Opened: ");
    serial_write(n ? n->name : "Untitled");
    serial_write("\n");
}
bool editor_has_unsaved(void) {
    extern Window *ui_order[6];
    extern int ui_count;
    for (int i = 0; i < ui_count; i++) {
        Window *w = ui_order[i];
        if (w->draw == draw && ((Editor *)w->state)->modified)
            return true;
    }
    return false;
}
