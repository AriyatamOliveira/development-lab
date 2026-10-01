#include "input.h"
#include "virtio.h"
typedef struct RawEvent {
    uint16_t type, code;
    uint32_t value;
} RawEvent;
typedef struct InputDevice {
    VDevice v;
    RawEvent events[VQ_SIZE];
} InputDevice;
static InputDevice devices[3];
static int device_count;
static InputEvent events[256];
static unsigned head, tail;
static int mx = 512, my = 384;
static bool shift, ctrl;
static void push(InputEvent e) {
    unsigned next = (head + 1) % 256;
    if (next != tail) {
        events[head] = e;
        head = next;
    }
}
bool input_next(InputEvent *e) {
    if (tail == head)
        return false;
    *e = events[tail];
    tail = (tail + 1) % 256;
    return true;
}
static void found(uintptr_t base, unsigned id) {
    if (id != 18 || device_count >= 3)
        return;
    InputDevice *d = &devices[device_count];
    if (!virtio_init(&d->v, base, 0) || !virtio_queue(&d->v, 0) || !virtio_queue(&d->v, 1))
        return;
    for (unsigned i = 0; i < VQ_SIZE; i++) {
        d->v.q[0].desc[i] = (struct VDesc){(uintptr_t)&d->events[i], sizeof(RawEvent), 2, 0};
        d->v.q[0].avail.ring[i] = i;
    }
    d->v.q[0].avail.idx = VQ_SIZE;
    virtio_ready(&d->v);
    mmio_write(base + 0x50, 0);
    device_count++;
}
void input_init(void) {
    virtio_scan(found);
}
int input_devices(void) {
    return device_count;
}
static int decode(unsigned code) {
    static const char numbers[] = "1234567890";
    static const char top[] = "qwertyuiop", mid[] = "asdfghjkl", bottom[] = "zxcvbnm";
    int c = 0;
    if (code >= 2 && code <= 11)
        c = shift ? "!@#$%^&*()"[code - 2] : numbers[code - 2];
    else if (code >= 16 && code <= 25)
        c = top[code - 16];
    else if (code >= 30 && code <= 38)
        c = mid[code - 30];
    else if (code >= 44 && code <= 50)
        c = bottom[code - 44];
    else
        switch (code) {
        case 1:
            return KEY_ESC;
        case 14:
            return 8;
        case 15:
            return 9;
        case 28:
            return 10;
        case 57:
            return ' ';
        case 12:
            return shift ? '_' : '-';
        case 13:
            return shift ? '+' : '=';
        case 26:
            return shift ? '{' : '[';
        case 27:
            return shift ? '}' : ']';
        case 39:
            return shift ? ':' : ';';
        case 40:
            return shift ? '"' : '\'';
        case 41:
            return shift ? '~' : '`';
        case 43:
            return shift ? '|' : '\\';
        case 51:
            return shift ? '<' : ',';
        case 52:
            return shift ? '>' : '.';
        case 53:
            return shift ? '?' : '/';
        case 103:
            return KEY_UP;
        case 108:
            return KEY_DOWN;
        case 105:
            return KEY_LEFT;
        case 106:
            return KEY_RIGHT;
        case 102:
            return KEY_HOME;
        case 107:
            return KEY_END;
        case 111:
            return KEY_DELETE;
        case 104:
            return KEY_PAGEUP;
        case 109:
            return KEY_PAGEDOWN;
        default:
            return 0;
        }
    if (c >= 'a' && c <= 'z' && shift)
        c -= 32;
    return c;
}
static void raw(RawEvent e) {
    InputEvent out = {.x = mx, .y = my, .ctrl = ctrl, .shift = shift};
    if (e.type == 1) {
        if (e.code == 42 || e.code == 54) {
            shift = e.value != 0;
            return;
        }
        if (e.code == 29 || e.code == 97) {
            ctrl = e.value != 0;
            return;
        }
        if (e.code == 272) {
            out.type = INPUT_BUTTON;
            out.down = e.value != 0;
            push(out);
            return;
        }
        if (e.value) {
            out.type = INPUT_KEY;
            out.key = decode(e.code);
            out.down = true;
            if (out.key)
                push(out);
        }
    } else if (e.type == 3 && (e.code == 0 || e.code == 1)) {
        if (e.code == 0)
            mx = (uint64_t)e.value * (1024 - 1) / 32767;
        else
            my = (uint64_t)e.value * (768 - 1) / 32767;
        if (mx < 0)
            mx = 0;
        if (mx > 1023)
            mx = 1023;
        if (my < 0)
            my = 0;
        if (my > 767)
            my = 767;
        out.type = INPUT_POINTER;
        out.x = mx;
        out.y = my;
        push(out);
    } else if (e.type == 2 && e.code == 8) {
        out.type = INPUT_SCROLL;
        out.key = (int32_t)e.value;
        push(out);
    }
}
void input_poll(void) {
    for (int i = 0; i < device_count; i++) {
        InputDevice *d = &devices[i];
        VQueue *q = &d->v.q[0];
        barrier();
        unsigned budget = VQ_SIZE;
        while (q->seen != q->used.idx && budget--) {
            unsigned id = q->used.ring[q->seen % VQ_SIZE].id;
            q->seen++;
            if (id >= VQ_SIZE)
                panic("Invalid input descriptor");
            barrier();
            raw(d->events[id]);
            virtio_submit(&d->v, 0, id);
        }
        uint32_t pending = mmio_read(d->v.base + 0x60);
        if (pending)
            mmio_write(d->v.base + 0x64, pending);
    }
}
