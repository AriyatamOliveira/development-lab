#ifndef INPUT_H
#define INPUT_H
#include "aion.h"
enum {
    KEY_LEFT = 256,
    KEY_RIGHT,
    KEY_UP,
    KEY_DOWN,
    KEY_HOME,
    KEY_END,
    KEY_DELETE,
    KEY_ESC,
    KEY_PAGEUP,
    KEY_PAGEDOWN
};
typedef struct InputEvent {
    int type, key, x, y;
    bool down, ctrl, shift;
} InputEvent;
enum { INPUT_KEY = 1, INPUT_POINTER, INPUT_BUTTON, INPUT_SCROLL };
void input_init(void);
void input_poll(void);
bool input_next(InputEvent *);
int input_devices(void);
#endif
