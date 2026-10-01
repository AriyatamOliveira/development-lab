#!/usr/bin/env python3
"""Interact with the real guest using QEMU keyboard/tablet events."""
import shutil, tempfile, time
from pathlib import Path
from qemu import VM, ROOT
from disk import files, snapshots
REPORT=ROOT/'build/verification'
REPORT.mkdir(parents=True,exist_ok=True)

def snap(vm,name):
 time.sleep(.15);vm.screenshot(REPORT/(name+'.ppm'))
 if shutil.which('sips'):
  import subprocess
  subprocess.run(['sips','-s','format','png',str(REPORT/(name+'.ppm')),'--out',str(REPORT/(name+'.png'))],stdout=subprocess.DEVNULL,check=True)

def login(vm):
 vm.wait('[SYSTEM] Boot complete');vm.click(512,470);vm.wait('[UI] Desktop entered')

def select_row(vm,index):vm.click(240,263+index*26)
def log(vm,name):(REPORT/(name+'.log')).write_text(vm.text())
with tempfile.TemporaryDirectory(prefix='aion-test-') as temp:
 image=Path(temp)/'disk.img'
 with image.open('wb') as f:f.truncate(4*1024*1024)
 with VM(image) as vm:
  vm.wait('[SYSTEM] Boot complete');snap(vm,'login');login(vm);snap(vm,'desktop')
  vm.click(60,130);vm.wait('[FILES] Window opened');select_row(vm,2);vm.click(124,484)
  vm.click(340,170);vm.type('Projects');vm.key('ret');vm.wait('[FILES] Folder created: Projects')
  vm.click(230,170);vm.type('Draft.txt');vm.key('ret');vm.wait('[FILES] File created: Draft.txt')
  vm.click(124,484);vm.wait('[EDITOR] Opened: Draft.txt')
  vm.type('Hello ARM64\nEdit me');vm.key('home');vm.type('Please ');vm.key('end');vm.key('backspace');vm.type('e');vm.key('shift-1')
  vm.click(480,224);vm.wait('[EDITOR] Saved: Draft.txt')
  vm.key('ctrl-shift-s');vm.type('/Documents/Final.txt');vm.key('ret');vm.wait('[EDITOR] Saved: Final.txt');snap(vm,'editor')
  expected='Hello ARM64\nPlease Edit me!'
  assert files(image)['/Documents/Draft.txt']['text']==expected,repr(files(image)['/Documents/Draft.txt']['text'])
  assert files(image)['/Documents/Final.txt']['text']==expected
  vm.click(940,180)
  select_row(vm,4);vm.click(472,170);vm.type('Renamed.txt');vm.key('ret');vm.wait('[FILES] Renamed: Renamed.txt')
  select_row(vm,3);vm.click(590,170);vm.key('ret');vm.wait('[FILES] Entry deleted')
  entries=files(image);assert '/Documents/Draft.txt' not in entries;assert entries['/Documents/Renamed.txt']['text']==expected
  # Create and delete an empty folder using the same native controls.
  select_row(vm,0);vm.click(590,170);vm.key('ret');time.sleep(.2);assert '/Documents/Projects' not in files(image)
  select_row(vm,2);vm.click(124,484);vm.wait('[EDITOR] Opened: Renamed.txt');snap(vm,'files-and-editor')
  # Window movement changes the actual framebuffer while retaining both apps.
  vm.move(350,180);vm.cmd('input-send-event',{'events':[{'type':'btn','data':{'button':'left','down':True}}]});vm.move(290,160);vm.cmd('input-send-event',{'events':[{'type':'btn','data':{'button':'left','down':False}}]});snap(vm,'dragged')
  # A dirty close shows a modal. Cancel keeps the document; confirm discards.
  vm.type('x');vm.click(880,160);vm.key('esc');assert vm.proc.poll() is None
  vm.click(880,160);vm.key('ret');time.sleep(.15)
  vm.click(900,746);vm.click(884,640);vm.wait('[POWER] Reboot')
  deadline=time.monotonic()+10
  while time.monotonic()<deadline and vm.text().count('[SYSTEM] Boot complete')<2:time.sleep(.05)
  assert vm.text().count('[SYSTEM] Boot complete')==2,vm.text()
  assert '[FS] Persistent snapshot loaded and validated' in vm.text();log(vm,'workflow-and-reboot')
  vm.click(512,470);vm.click(900,746);vm.click(884,684);vm.proc.wait(timeout=5);assert vm.proc.returncode==0;log(vm,'shutdown')
 with VM(image) as vm:
  login(vm);assert '[FS] Persistent snapshot loaded and validated' in vm.text()
  vm.click(60,250);vm.key('ctrl-o');vm.type('/Documents/Renamed.txt');vm.key('ret');vm.wait('[EDITOR] Opened: Renamed.txt');snap(vm,'persistent-reload');log(vm,'persistent-reload')
 assert files(image)['/Documents/Renamed.txt']['text']==expected
 # Corrupt the newest snapshot's payload. The kernel must load the older slot.
 valid=snapshots(image);assert len(valid)==2
 _,slot,_=valid[0]
 with image.open('r+b') as f:f.seek(slot*1024*1024+512+100);b=f.read(1);f.seek(-1,1);f.write(bytes([b[0]^1]))
 with VM(image) as vm:
  vm.wait('[SYSTEM] Boot complete');assert '[FS] Persistent snapshot loaded and validated' in vm.text();assert f'[FS] Snapshot generation: {valid[1][0]}' in vm.text();log(vm,'snapshot-recovery')
 with VM() as vm:
  vm.wait('[SYSTEM] Boot complete');assert '[FS] No writable flush-capable disk; RAM filesystem' in vm.text();log(vm,'ram-only')
print('PASS: boot, login, windows, folders, file lifecycle, editing, Save As, disk reload, reboot, shutdown, snapshot recovery, RAM fallback.')
print(f'Logs and screenshots: {REPORT}')
