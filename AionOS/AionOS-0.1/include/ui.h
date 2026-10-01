#ifndef UI_H
#define UI_H
#include "graphics.h"
#include "input.h"
typedef struct Window Window;
struct Window {
    bool alive;
    int x, y, w, h;
    char title[64];
    void *state;
    void (*draw)(Window *);
    void (*event)(Window *, InputEvent);
    bool (*close)(Window *);
};
typedef bool (*PromptAction)(const char *, void *);
void ui_init(void);
void ui_task(void *);
void input_task(void *);
Window *ui_window(const char *, int, int, int, int, size_t);
void ui_destroy(Window *);
void ui_dirty(void);
void ui_status(const char *);
void ui_prompt(const char *, const char *, PromptAction, void *);
void ui_confirm(const char *, PromptAction, void *);
bool ui_inside(int, int, int, int, int, int);
void ui_button(int, int, int, int, const char *, bool);
void ui_label(Window *, int, int, const char *, uint32_t);
void ui_local_button(Window *, int, int, int, const char *, bool);
void file_manager_open(void);
void editor_open(int);
bool editor_has_unsaved(void);
#endif
