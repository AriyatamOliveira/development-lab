#!/usr/bin/env python3
"""Create a new blank AionOS image. Never truncate an existing file."""
import argparse
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('path',nargs='?',default='data/aion-disk.img');a=p.parse_args();path=Path(a.path);path.parent.mkdir(parents=True,exist_ok=True)
if path.exists():
 if path.stat().st_size<4*1024*1024:raise SystemExit(f'{path}: existing image is too small; preserved unchanged')
 print(f'Using existing disk: {path}')
else:
 with path.open('xb') as f:f.truncate(4*1024*1024)
 print(f'Created blank 4 MiB disk: {path}')
