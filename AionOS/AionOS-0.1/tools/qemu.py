"""QEMU test controller. Tests drive the actual bare-metal kernel's devices."""

import json
import select
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class VM:
    def __init__(self, disk=None, kernel=None, display="none"):
        self.tmp = tempfile.TemporaryDirectory(prefix="aion-", dir="/tmp")
        self.path = Path(self.tmp.name)
        self.log = open(self.path / "serial.log", "w+")
        qemu = shutil.which("qemu-system-aarch64") or "/opt/homebrew/bin/qemu-system-aarch64"
        command = [
            qemu, "-machine", "virt,gic-version=2", "-cpu", "cortex-a57",
            "-accel", "tcg", "-m", "256M", "-smp", "1",
            "-kernel", str(kernel or ROOT / "build/aion.elf"),
            "-display", display, "-device", "ramfb",
            "-global", "virtio-mmio.force-legacy=false",
            "-device", "virtio-keyboard-device", "-device", "virtio-tablet-device",
            "-serial", f"file:{self.path}/serial.log", "-monitor", "none", "-qmp", "stdio",
        ]
        if disk:
            command += [
                "-drive", f"if=none,id=storage,format=raw,file={disk}",
                "-device", "virtio-blk-device,drive=storage",
            ]
        self.proc = subprocess.Popen(
            command, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=self.log, bufsize=0,
        )
        self.read()
        self.cmd("qmp_capabilities")

    def read(self):
        if not select.select([self.proc.stdout], [], [], 8)[0]:
            raise TimeoutError("QMP reply timed out")
        data = self.proc.stdout.readline()
        if not data:
            raise RuntimeError("QEMU stopped: " + self.text())
        return json.loads(data)

    def cmd(self, name, args=None):
        message = json.dumps({"execute": name, "arguments": args or {}}) + "\n"
        self.proc.stdin.write(message.encode())
        self.proc.stdin.flush()
        while True:
            reply = self.read()
            if "error" in reply:
                raise RuntimeError(reply)
            if "return" in reply:
                return reply["return"]

    def text(self):
        self.log.flush()
        return (self.path / "serial.log").read_text()

    def wait(self, marker, timeout=8):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            text = self.text()
            if marker in text:
                return text
            if "PANIC:" in text:
                raise AssertionError(text)
            time.sleep(0.05)
        raise AssertionError(f"Timeout waiting for {marker}\n{self.text()}")

    def screenshot(self, path):
        self.cmd("screendump", {"filename": str(Path(path).resolve())})

    def key(self, key):
        # Send complete device key transitions rather than depending on a
        # host/guest timer race for the release of a held key.
        codes = key.split("-")
        events = []
        for code in codes:
            events.append({"type": "key", "data": {
                "down": True, "key": {"type": "qcode", "data": code}}})
        for code in reversed(codes):
            events.append({"type": "key", "data": {
                "down": False, "key": {"type": "qcode", "data": code}}})
        self.cmd("input-send-event", {"events": events})
        time.sleep(0.14)

    def type(self, text):
        symbols = {
            " ": "spc", "\n": "ret", ".": "dot", "-": "minus",
            "/": "slash", "_": "shift-minus", ":": "shift-semicolon",
        }
        for character in text:
            key = symbols.get(character, "shift-" + character.lower()
                              if character.isupper() else character)
            self.key(key)

    def move(self, x, y):
        self.cmd("input-send-event", {"events": [
            {"type": "abs", "data": {"axis": "x", "value": int(x * 32767 / 1023)}},
            {"type": "abs", "data": {"axis": "y", "value": int(y * 32767 / 767)}},
        ]})
        time.sleep(0.08)

    def click(self, x, y):
        self.move(x, y)
        for down in (True, False):
            # Poweroff can exit QEMU on button-down; no release is then needed.
            if self.proc.poll() is not None:
                break
            self.cmd("input-send-event", {"events": [{"type": "btn", "data": {
                "down": down, "button": "left"}}]})
            time.sleep(0.12)

    def close(self):
        if self.proc.poll() is None:
            self.proc.terminate()
        self.proc.wait(timeout=5)
        try:
            self.proc.stdin.close()
        except BrokenPipeError:
            pass
        self.proc.stdout.close()
        self.log.close()
        self.tmp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
