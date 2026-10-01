#ifndef FS_H
#define FS_H
#include "aion.h"
#define FS_NODES 64
#define FS_NAME 48
#define FS_DATA 4096
typedef struct FsNode {
    uint8_t used, dir;
    uint16_t parent;
    uint32_t size, identity;
    char name[FS_NAME];
    char data[FS_DATA];
} FsNode;
void fs_init(void);
void fs_mount_disk(void);
const FsNode *fs_node(int);
int fs_find(int, const char *);
int fs_lookup(const char *);
int fs_create(int, const char *, bool);
bool fs_write(int, const char *, size_t);
bool fs_rename(int, const char *);
bool fs_delete(int);
int fs_list(int, int *, int);
void fs_path(int, char *, size_t);
const char *fs_error(void);
uint64_t fs_revision(void);
const void *fs_image(void);
size_t fs_image_size(void);
bool fs_import(const void *, size_t);
bool fs_sync(void);
bool fs_persistent(void);
#endif
