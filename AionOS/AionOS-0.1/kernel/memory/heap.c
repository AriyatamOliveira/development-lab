#include "aion.h"
typedef struct Block {
    size_t size;
    struct Block *next;
    bool free;
    uint64_t pad;
} Block;
static unsigned char arena[1024 * 1024] __attribute__((aligned(16)));
static Block *head;
void *kmalloc(size_t n) {
    if (!n || n > sizeof arena - sizeof(Block))
        return NULL;
    n = (n + 15) & ~15UL;
    if (!head) {
        head = (Block *)arena;
        head->size = sizeof arena - sizeof(Block);
        head->free = true;
        head->next = NULL;
    }
    for (Block *b = head; b; b = b->next)
        if (b->free && b->size >= n) {
            if (b->size >= n + sizeof(Block) + 16) {
                Block *tail = (Block *)((char *)(b + 1) + n);
                tail->size = b->size - n - sizeof(Block);
                tail->next = b->next;
                tail->free = true;
                b->next = tail;
                b->size = n;
            }
            b->free = false;
            return b + 1;
        }
    return NULL;
}
void kfree(void *p) {
    if (!p)
        return;
    Block *found = NULL;
    for (Block *b = head; b; b = b->next)
        if (b + 1 == p) {
            found = b;
            break;
        }
    ASSERT(found && !found->free);
    found->free = true;
    for (Block *b = head; b && b->next;)
        if (b->free && b->next->free) {
            b->size += sizeof(Block) + b->next->size;
            b->next = b->next->next;
        } else
            b = b->next;
}
