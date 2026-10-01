#include "fs.h"
#include <stdio.h>
#include <stdlib.h>
void panic(const char *s) {
    fprintf(stderr, "%s\n", s);
    exit(1);
}
int main(void) {
    // Check the runtime's optimized word paths at aligned and unaligned offsets.
    unsigned char source[320], destination[320];
    for (unsigned i = 0; i < 320; i++)
        source[i] = (unsigned char)i;
    for (unsigned offset = 0; offset < 16; offset++)
        for (unsigned size = 0; size < 256; size++) {
            memset(destination, 0x5a, sizeof destination);
            memcpy(destination + offset, source + offset, size);
            for (unsigned i = 0; i < 320; i++)
                ASSERT(destination[i] == (i >= offset && i < offset + size ? source[i] : 0x5a));
        }
    void *blocks[2048];
    int allocated = 0;
    while (allocated < 2048 && (blocks[allocated] = kmalloc(1000))) {
        ASSERT(((uintptr_t)blocks[allocated] & 15) == 0);
        allocated++;
    }
    ASSERT(allocated > 900);
    for (int i = 0; i < allocated; i += 2)
        kfree(blocks[i]);
    for (int i = 1; i < allocated; i += 2)
        kfree(blocks[i]);
    void *big = kmalloc(900000);
    ASSERT(big);
    kfree(big);
    fs_init();
    int docs = fs_lookup("/Documents");
    ASSERT(docs > 0);
    ASSERT(fs_lookup("/Documents/../System") > 0);
    int f = fs_create(docs, "test.txt", false);
    ASSERT(f > 0);
    ASSERT(fs_create(docs, "test.txt", false) < 0);
    ASSERT(fs_write(f, "first\nsecond", 12));
    ASSERT(!strcmp(fs_node(f)->data, "first\nsecond"));
    ASSERT(fs_rename(f, "renamed.txt"));
    ASSERT(fs_lookup("/Documents/renamed.txt") == f);
    ASSERT(!fs_rename(f, "../bad"));
    ASSERT(!fs_delete(docs));
    int folder = fs_create(docs, "Folder", true);
    ASSERT(folder > 0);
    int child = fs_create(folder, "inside.txt", false);
    ASSERT(child > 0);
    ASSERT(!fs_delete(folder));
    ASSERT(fs_delete(child));
    ASSERT(fs_delete(folder));
    ASSERT(fs_delete(f));
    ASSERT(!fs_node(f));
    ASSERT(fs_create(docs, "", false) < 0);
    ASSERT(fs_create(docs, "..", false) < 0);
    char *copy = malloc(fs_image_size());
    memcpy(copy, fs_image(), fs_image_size());
    ASSERT(fs_import(copy, fs_image_size()));
    ((FsNode *)copy)[0].dir = 0;
    ASSERT(!fs_import(copy, fs_image_size()));
    memcpy(copy, fs_image(), fs_image_size());
    ((FsNode *)copy)[5].parent = 5;
    ASSERT(!fs_import(copy, fs_image_size()));
    memcpy(copy, fs_image(), fs_image_size());
    ((FsNode *)copy)[3].parent = 65535;
    ASSERT(!fs_import(copy, fs_image_size()));
    free(copy);
    char large[FS_DATA];
    memset(large, 'x', sizeof large);
    f = fs_create(docs, "limit.txt", false);
    ASSERT(!fs_write(f, large, FS_DATA));
    ASSERT(fs_write(f, large, FS_DATA - 1));
    ASSERT(fs_node(f)->data[FS_DATA - 1] == 0);
    char path[128];
    fs_path(f, path, sizeof path);
    ASSERT(!strcmp(path, "/Documents/limit.txt"));
    while (fs_create(docs, "occupied", false) >= 0) {
    } // Duplicate must fail immediately.
    for (int i = 0; i < 100; i++) {
        char name[32], n[16];
        number(n, i, 10);
        strcopy(name, "entry", sizeof name);
        size_t len = strlen(name);
        strcopy(name + len, n, sizeof(name) - len);
        fs_create(docs, name, false);
    }
    ASSERT(fs_create(docs, "overflow", false) < 0);
    puts("Runtime/heap/filesystem tests passed: lifecycle, validation, hierarchy, snapshots and "
         "limits.");
    return 0;
}
