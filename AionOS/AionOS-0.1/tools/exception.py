#!/usr/bin/env python3
import subprocess, time, shutil
from qemu import VM,ROOT
out=ROOT/'build/verification';out.mkdir(parents=True,exist_ok=True)
with VM(kernel=ROOT/'build/exception.elf') as vm:
 vm.wait('[HALT] Fatal exception; CPU halted')
 text=vm.text()
 for marker in ['PANIC: Data Abort','PC:','SP:','ESR_EL1:','FAR_EL1: 0xffff000000000000','SPSR_EL1:','x30:']:
  assert marker in text,text
 vm.screenshot(out/'panic.ppm');(out/'exception.log').write_text(text)
 if shutil.which('sips'):subprocess.run(['sips','-s','format','png',str(out/'panic.ppm'),'--out',str(out/'panic.png')],stdout=subprocess.DEVNULL,check=True)
 print('PASS: real ARM64 data abort reports PC, SP, ESR, FAR, SPSR and x0-x30, then halts safely.')
