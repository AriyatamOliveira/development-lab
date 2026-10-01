.section .text.boot
.global _start
_start:
    // One CPU owns initialization. Secondary CPUs stay parked.
    mrs x1, mpidr_el1
    and x1, x1, #0xff
    cbnz x1, park
    mov x20, x0
    msr daifset, #0xf
    mrs x1, CurrentEL
    cmp x1, #0x8
    b.ne el1
    // Permit EL1 access to the counter, and enter EL1h with IRQs masked.
    mov x1, #3
    msr cnthctl_el2, x1
    msr cntvoff_el2, xzr
    mov x1, #(1 << 31)
    msr hcr_el2, x1
    adr x1, el1
    msr elr_el2, x1
    mov x1, #0x3c5
    msr spsr_el2, x1
    eret
el1:
    ldr x1, =__stack_top
    mov sp, x1
    // QEMU may leave floating point disabled. C is compiled without SIMD.
    ldr x1, =__bss_start
    ldr x2, =__bss_end
1:  cmp x1, x2
    b.hs 2f
    str xzr, [x1], #8
    b 1b
2:  mov x0, x20
    bl kernel_main
park:
    wfe
    b park
