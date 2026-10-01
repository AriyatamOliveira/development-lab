#include "fs.h"
static FsNode nodes[FS_NODES];
static char error[80];
static uint64_t revision;
static uint32_t identity;
static bool fail(const char *s) {
    strcopy(error, s, sizeof error);
    return false;
}
const char *fs_error(void) {
    return error;
}
uint64_t fs_revision(void) {
    return revision;
}
const FsNode *fs_node(int id) {
    return id >= 0 && id < FS_NODES && nodes[id].used ? &nodes[id] : NULL;
}
static bool directory(int id) {
    const FsNode *n = fs_node(id);
    return n && n->dir;
}
static bool name_valid(const char *name) {
    size_t len = strlen(name);
    if (!len || len >= FS_NAME)
        return fail("Name must contain 1 to 47 characters.");
    if (!strcmp(name, ".") || !strcmp(name, ".."))
        return fail("That name is reserved.");
    for (size_t i = 0; i < len; i++)
        if (name[i] == '/' || (unsigned char)name[i] < 32 || (unsigned char)name[i] > 126)
            return fail("Use printable ASCII names without /.");
    return true;
}
int fs_find(int parent, const char *name) {
    for (int i = 1; i < FS_NODES; i++)
        if (nodes[i].used && nodes[i].parent == parent && !strcmp(nodes[i].name, name))
            return i;
    return -1;
}
int fs_lookup(const char *path) {
    if (!path || path[0] != '/')
        return -1;
    int dir = 0;
    path++;
    while (*path) {
        char name[FS_NAME];
        unsigned i = 0;
        while (*path && *path != '/') {
            if (i + 1 >= sizeof name)
                return -1;
            name[i++] = *path++;
        }
        name[i] = 0;
        if (!directory(dir))
            return -1;
        if (i) {
            if (!strcmp(name, ".."))
                dir = nodes[dir].parent;
            else if (strcmp(name, "."))
                dir = fs_find(dir, name);
            if (dir < 0)
                return -1;
        }
        if (*path == '/')
            path++;
    }
    return dir;
}
int fs_create(int parent, const char *name, bool dir) {
    if (!directory(parent)) {
        fail("Parent directory no longer exists.");
        return -1;
    }
    if (!name_valid(name))
        return -1;
    if (fs_find(parent, name) >= 0) {
        fail("A file or folder already has that name.");
        return -1;
    }
    if (identity == UINT32_MAX) {
        fail("Filesystem identity counter exhausted.");
        return -1;
    }
    for (int i = 1; i < FS_NODES; i++)
        if (!nodes[i].used) {
            FsNode *n = &nodes[i];
            memset(n, 0, sizeof *n);
            n->used = 1;
            n->dir = dir;
            n->parent = parent;
            n->identity = ++identity;
            strcopy(n->name, name, sizeof n->name);
            revision++;
            return i;
        }
    fail("Filesystem is full (64 entries).");
    return -1;
}
bool fs_write(int id, const char *data, size_t size) {
    const FsNode *n = fs_node(id);
    if (!n || n->dir)
        return fail("Text file no longer exists.");
    if (size >= FS_DATA)
        return fail("Text files are limited to 4095 bytes.");
    memcpy(nodes[id].data, data, size);
    nodes[id].data[size] = 0;
    nodes[id].size = size;
    revision++;
    return true;
}
bool fs_rename(int id, const char *name) {
    const FsNode *n = fs_node(id);
    if (!n)
        return fail("Entry no longer exists.");
    if (id <= 4)
        return fail("Default system directories are protected.");
    if (!name_valid(name))
        return false;
    int duplicate = fs_find(n->parent, name);
    if (duplicate >= 0 && duplicate != id)
        return fail("That name already exists.");
    strcopy(nodes[id].name, name, FS_NAME);
    revision++;
    return true;
}
bool fs_delete(int id) {
    const FsNode *n = fs_node(id);
    if (!n)
        return fail("Entry no longer exists.");
    if (id <= 4)
        return fail("Default system directories are protected.");
    if (n->dir)
        for (int i = 1; i < FS_NODES; i++)
            if (nodes[i].used && nodes[i].parent == id)
                return fail("Remove the folder's contents first.");
    memset(&nodes[id], 0, sizeof nodes[id]);
    revision++;
    return true;
}
int fs_list(int dir, int *out, int cap) {
    if (!directory(dir))
        return 0;
    int count = 0;
    for (int pass = 0; pass < 2; pass++)
        for (int i = 1; i < FS_NODES; i++)
            if (nodes[i].used && nodes[i].parent == dir && (nodes[i].dir ? 0 : 1) == pass) {
                if (count < cap)
                    out[count] = i;
                count++;
            }
    return count < cap ? count : cap;
}
void fs_path(int id, char *out, size_t cap) {
    int chain[FS_NODES], n = 0;
    while (id > 0 && fs_node(id) && n < FS_NODES) {
        chain[n++] = id;
        id = nodes[id].parent;
    }
    size_t used = 0;
    if (cap < 2) {
        if (cap)
            out[0] = 0;
        return;
    }
    out[used++] = '/';
    while (n) {
        const char *s = nodes[chain[--n]].name;
        while (*s && used + 1 < cap)
            out[used++] = *s++;
        if (n && used + 1 < cap)
            out[used++] = '/';
    }
    out[used] = 0;
}
void fs_init(void) {
    memset(nodes, 0, sizeof nodes);
    revision = 0;
    identity = 1;
    nodes[0].used = 1;
    nodes[0].dir = 1;
    nodes[0].identity = 1;
    strcopy(nodes[0].name, "/", FS_NAME);
    fs_create(0, "System", true);
    fs_create(0, "Applications", true);
    int docs = fs_create(0, "Documents", true);
    fs_create(0, "Desktop", true);
    int f = fs_create(docs, "Welcome.txt", false);
    const char *welcome =
        "Welcome to AionOS!\n\nThis is an original ARM64 operating system.\nYour kernel draws "
        "every pixel of this desktop.\n\nUse File Manager to create folders and text files.\nOpen "
        "a file, edit it, and click Save.\nCtrl+S saves. Ctrl+Shift+S opens Save As.\n\nHave fun "
        "learning how an OS works.\n";
    fs_write(f, welcome, strlen(welcome));
    f = fs_create(docs, "Notes.txt", false);
    const char *notes = "Things to explore\n\n- Drag a window by its title bar.\n- Create a new "
                        "text file.\n- Rename a file in File Manager.\n- Try the Power menu.\n";
    fs_write(f, notes, strlen(notes));
    f = fs_create(1, "About.txt", false);
    const char *about = "AionOS 0.1\nFreestanding AArch64 C kernel.\nNo Linux, BSD, XNU, or OS "
                        "framework.\nApplications run as trusted kernel code.\n";
    fs_write(f, about, strlen(about));
}
const void *fs_image(void) {
    return nodes;
}
size_t fs_image_size(void) {
    return sizeof nodes;
}
bool fs_import(const void *image, size_t size) {
    if (size != sizeof nodes)
        return fail("Invalid snapshot length.");
    const FsNode *p = image;
    if (!p[0].used || p[0].dir != 1 || p[0].parent != 0)
        return fail("Invalid root directory.");
    uint32_t highest = 1;
    for (int i = 0; i < FS_NODES; i++)
        if (p[i].used) {
            if (p[i].used != 1 || p[i].dir > 1 || !p[i].identity || p[i].size >= FS_DATA)
                return fail("Invalid entry in snapshot.");
            bool term = false;
            for (int j = 0; j < FS_NAME; j++)
                if (!p[i].name[j]) {
                    term = true;
                    break;
                }
            if (!term)
                return fail("Unterminated filename.");
            if (i && (!name_valid(p[i].name) || p[i].parent >= FS_NODES || !p[p[i].parent].used ||
                      !p[p[i].parent].dir))
                return fail("Invalid parent directory.");
            if (!p[i].dir && p[i].data[p[i].size])
                return fail("Unterminated text file.");
            int parent = i;
            for (int n = 0; parent && n <= FS_NODES; n++) {
                if (parent < 0 || parent >= FS_NODES || !p[parent].used ||
                    (!p[parent].dir && parent != i))
                    return fail("Invalid ancestor in snapshot.");
                parent = p[parent].parent;
                if (n == FS_NODES)
                    return fail("Directory cycle in snapshot.");
            }
            for (int j = 0; j < i; j++)
                if (p[j].used &&
                    (p[j].identity == p[i].identity ||
                     (i && j && p[j].parent == p[i].parent && !strcmp(p[j].name, p[i].name))))
                    return fail("Duplicate snapshot entry.");
            if (p[i].identity > highest)
                highest = p[i].identity;
        }
    if (highest == UINT32_MAX)
        return fail("Identity counter exhausted.");
    memcpy(nodes, image, sizeof nodes);
    identity = highest;
    revision++;
    return true;
}
