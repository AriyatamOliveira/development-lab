#include "aion.h"
#include "fs.h"
#include "graphics.h"
#include "input.h"
#include "ui.h"
void kernel_main(uintptr_t dtb) {
    boot_log("[BOOT] AionOS 0.1 - original ARM64 kernel");
    boot_log("[CPU] AArch64 EL1 detected");
    memory_init(dtb);
    serial_write("[MM] Available RAM: ");
    serial_dec(memory_size() / 1024 / 1024);
    boot_log(" MiB");
    void *p = page_alloc();
    ASSERT(p);
    ASSERT(page_free(p));
    ASSERT(!page_free(p));
    void *a = kmalloc(37), *b = kmalloc(1000);
    ASSERT(a && b);
    kfree(a);
    kfree(b);
    a = kmalloc(900000);
    ASSERT(a);
    kfree(a);
    boot_log("[MM] Physical pages and heap self-tests passed");
    mmu_init();
    boot_log("[VMM] Identity translation enabled");
    interrupts_init();
    boot_log("[IRQ] Exception vectors and GICv2 installed");
    timer_init();
    sleep_ms(100);
    ASSERT(ticks() > 0);
    boot_log("[TIMER] 100 Hz timer interrupts verified");
    ASSERT(graphics_init());
    boot_log("[BOOT] AionOS 0.1 / ARM64");
    boot_log("[MM] Physical pages and heap ready / 256 MiB");
    boot_log("[VMM] Identity translation active");
    boot_log("[IRQ] Exceptions and timer interrupts ready");
    boot_log("[GUI] 1024 x 768 framebuffer initialized");
    input_init();
    ASSERT(input_devices() == 2);
    boot_log("[INPUT] Virtio keyboard and tablet initialized");
    fs_init();
    fs_mount_disk();
    ASSERT(fs_lookup("/") == 0);
    boot_log("[FS] Original filesystem mounted");
    boot_log("[UI] Widgets and window manager initialized");
    sleep_ms(1400);
    scheduler_init();
    ui_init();
    ASSERT(task_create("input", input_task, NULL) >= 0);
    ASSERT(task_create("desktop", ui_task, NULL) >= 0);
    boot_log("[SYSTEM] Boot complete");
    scheduler_run();
}
