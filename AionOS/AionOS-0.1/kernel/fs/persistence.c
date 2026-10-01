#include "fs.h"
#include "virtio.h"
#define SLOT_SECTORS 2048
#define IMAGE_CAPACITY (FS_NODES * sizeof(FsNode) + 511)
typedef struct DiskHeader {
    char magic[8];
    uint32_t version, length, crc, reserved;
    uint64_t generation;
    uint32_t header_crc;
    uint8_t pad[476];
} DiskHeader;
_Static_assert(sizeof(FsNode) == 4156, "Node layout must match disk format");
_Static_assert(sizeof(DiskHeader) == 512, "Disk header must occupy one sector");
static uint8_t snapshot[IMAGE_CAPACITY] __attribute__((aligned(4096)));
static DiskHeader headers[2];
static bool writable;
static int active = -1;
static uint64_t generation;
static uint32_t crc32(const void *buffer, size_t n) {
    const uint8_t *p = buffer;
    uint32_t crc = ~0u;
    while (n--) {
        crc ^= *p++;
        for (int i = 0; i < 8; i++)
            crc = (crc >> 1) ^ (0xedb88320u & (0u - (crc & 1)));
    }
    return ~crc;
}
static bool valid_header(DiskHeader *h) {
    return h->magic[0] == 'A' && h->magic[1] == 'I' && h->magic[2] == 'O' && h->magic[3] == 'N' &&
           h->magic[4] == 'F' && h->magic[5] == 'S' && h->magic[6] == '1' && h->magic[7] == 0 &&
           h->version == 1 && h->length == fs_image_size() && h->generation &&
           h->header_crc == crc32(h, 32);
}
static bool load_slot(int slot) {
    DiskHeader *h = &headers[slot];
    if (!valid_header(h))
        return false;
    uint32_t size = (h->length + 511) & ~511u;
    if (!block_transfer(false, slot * SLOT_SECTORS + 1, snapshot, size) ||
        crc32(snapshot, h->length) != h->crc)
        return false;
    if (!fs_import(snapshot, h->length))
        return false;
    active = slot;
    generation = h->generation;
    return true;
}
void fs_mount_disk(void) {
    writable = false;
    active = -1;
    generation = 0;
    if (!block_init() || block_capacity() < 2 * SLOT_SECTORS || !block_flush()) {
        boot_log("[FS] No writable flush-capable disk; RAM filesystem");
        return;
    }
    bool reads = true;
    for (int i = 0; i < 2; i++)
        if (!block_transfer(false, i * SLOT_SECTORS, &headers[i], 512))
            reads = false;
    if (!reads) {
        boot_log("[FS] Disk read failed; preserving disk, using RAM");
        return;
    }
    int preferred = headers[1].generation > headers[0].generation ? 1 : 0;
    if (load_slot(preferred) || load_slot(1 - preferred)) {
        writable = true;
        boot_log("[FS] Persistent snapshot loaded and validated");
        serial_write("[FS] Snapshot generation: ");
        serial_dec(generation);
        serial_write(" / slot ");
        serial_dec(active);
        serial_write("\n");
        return;
    }
    // A new image has zero header sectors. Never automatically format an
    // unrecognized or damaged disk: the launcher creates an explicit blank image.
    bool blank = true;
    for (int i = 0; i < 2; i++)
        for (unsigned j = 0; j < sizeof(DiskHeader); j++)
            if (((uint8_t *)&headers[i])[j])
                blank = false;
    if (!blank) {
        boot_log("[FS] Invalid disk snapshots; disk preserved, using RAM");
        return;
    }
    writable = true;
    if (!fs_sync()) {
        writable = false;
        boot_log("[FS] Initial disk format failed; using RAM");
    } else
        boot_log("[FS] Blank disk initialized with default files");
}
bool fs_persistent(void) {
    return writable;
}
bool fs_sync(void) {
    if (!writable)
        return true;
    int target = active == 0 ? 1 : 0;
    uint32_t n = fs_image_size(), bytes = (n + 511) & ~511u;
    DiskHeader *h = &headers[target];
    memset(h, 0, sizeof *h);
    // Invalidate the old target first. The active snapshot remains untouched.
    if (!block_transfer(true, target * SLOT_SECTORS, h, 512) || !block_flush())
        return false;
    memset(snapshot, 0, bytes);
    memcpy(snapshot, fs_image(), n);
    if (!block_transfer(true, target * SLOT_SECTORS + 1, snapshot, bytes) || !block_flush())
        return false;
    memcpy(h->magic, "AIONFS1", 8);
    h->version = 1;
    h->length = n;
    h->crc = crc32(snapshot, n);
    h->generation = generation + 1;
    h->header_crc = crc32(h, 32);
    if (!block_transfer(true, target * SLOT_SECTORS, h, 512) || !block_flush())
        return false;
    active = target;
    generation = h->generation;
    return true;
}
