#include "aion.h"
#define TASKS 8
#define STACK_SIZE 16384
typedef struct Context {
    uint64_t registers[12], sp;
} Context;
typedef struct Task {
    Context ctx;
    char name[32];
    void (*entry)(void *);
    void *arg;
    bool alive;
} Task;
static Task tasks[TASKS];
static Context boot_context;
static int current = -1;
static unsigned char stacks[TASKS][STACK_SIZE] __attribute__((aligned(16)));
extern void context_switch(Context *, Context *);
static void task_start(void) {
    Task *t = &tasks[current];
    t->entry(t->arg);
    t->alive = false;
    task_yield();
    panic("Exited task resumed");
}
void scheduler_init(void) {
    memset(tasks, 0, sizeof tasks);
    current = -1;
}
int task_create(const char *name, void (*fn)(void *), void *arg) {
    for (int i = 0; i < TASKS; i++)
        if (!tasks[i].alive) {
            Task *t = &tasks[i];
            memset(t, 0, sizeof *t);
            strcopy(t->name, name, sizeof t->name);
            t->entry = fn;
            t->arg = arg;
            t->alive = true;
            t->ctx.sp = (uintptr_t)&stacks[i][STACK_SIZE];
            t->ctx.registers[11] = (uintptr_t)task_start;
            return i;
        }
    return -1;
}
void task_yield(void) {
    int old = current, next = -1;
    for (int n = 1; n <= TASKS; n++) {
        int i = (old + n) % TASKS;
        if (i < 0)
            i += TASKS;
        if (tasks[i].alive) {
            next = i;
            break;
        }
    }
    if (next < 0)
        panic("No runnable kernel tasks");
    if (next == old)
        return;
    current = next;
    context_switch(old < 0 ? &boot_context : &tasks[old].ctx, &tasks[next].ctx);
}
void scheduler_run(void) {
    task_yield();
    panic("Scheduler unexpectedly returned");
}
