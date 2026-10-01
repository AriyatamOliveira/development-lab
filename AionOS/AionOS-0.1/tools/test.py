#!/usr/bin/env python3
import subprocess
from pathlib import Path
root=Path(__file__).resolve().parents[1]
(root/'build').mkdir(exist_ok=True)
subprocess.run(['clang','-std=c11','-fno-builtin','-fsanitize=address,undefined','-g','-Wall','-Wextra','-Iinclude','kernel/fs/fs.c','kernel/memory/heap.c','kernel/lib.c','tests/fs_test.c','-o','build/fs_test'],cwd=root,check=True)
subprocess.run([str(root/'build/fs_test')],check=True)
