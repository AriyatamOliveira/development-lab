CLANG := $(shell command -v /opt/homebrew/opt/llvm/bin/clang 2>/dev/null || command -v clang)
LD := $(shell command -v /opt/homebrew/opt/lld/bin/ld.lld 2>/dev/null || command -v ld.lld)
CFLAGS := --target=aarch64-none-elf -mcpu=cortex-a57 -mgeneral-regs-only -ffreestanding -fno-builtin -fno-stack-protector -fno-pic -nostdlib -O2 -g -Wall -Wextra -Werror -Iinclude -MMD -MP
SOURCES := $(shell find boot kernel apps -name '*.c' -o -name '*.S')
OBJECTS := $(addprefix build/,$(addsuffix .o,$(SOURCES)))
.PHONY: all clean run debug test smoke exception-check
all: build/aion.elf
build/aion.elf: $(OBJECTS) boot/linker.ld
	$(LD) -nostdlib -T boot/linker.ld -Map=build/aion.map $(OBJECTS) -o $@
build/%.c.o: %.c
	@mkdir -p $(dir $@)
	$(CLANG) $(CFLAGS) -c $< -o $@
build/%.S.o: %.S
	@mkdir -p $(dir $@)
	$(CLANG) $(CFLAGS) -c $< -o $@
clean:
	rm -rf build
run: all
	./run.sh
debug: all
	./run.sh --debug
test:
	python3 tools/test.py
smoke: all
	python3 tools/smoke.py
-include $(OBJECTS:.o=.d)

build/exception.elf: $(filter-out build/kernel/main.c.o,$(OBJECTS)) build/tests/exception_entry.c.o boot/linker.ld
	$(LD) -nostdlib -T boot/linker.ld $(filter-out build/kernel/main.c.o,$(OBJECTS)) build/tests/exception_entry.c.o -o $@
exception-check: build/exception.elf
	python3 tools/exception.py
