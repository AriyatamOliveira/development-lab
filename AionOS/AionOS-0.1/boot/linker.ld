ENTRY(_start)
SECTIONS {
  . = 0x40080000;
  __kernel_start = .;
  .text : { KEEP(*(.text.boot)) *(.text .text.*) }
  .rodata : { *(.rodata .rodata.*) }
  .data : { *(.data .data.*) }
  . = ALIGN(4096);
  .bss (NOLOAD) : { __bss_start = .; *(.bss .bss.* COMMON) . = ALIGN(16); __bss_end = .; }
  .stack (NOLOAD) : { . += 65536; __stack_top = .; }
  . = ALIGN(4096);
  __kernel_end = .;
  /DISCARD/ : { *(.comment) *(.eh_frame*) *(.note*) }
}
