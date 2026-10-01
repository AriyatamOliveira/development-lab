"""Inspect AionOS snapshots without mounting the image on the host."""
import argparse, struct, zlib
from pathlib import Path
NODE=struct.Struct('<BBHII48s4096s')
SLOT_BYTES=1024*1024

def snapshots(path):
 data=Path(path).read_bytes();valid=[]
 for slot in range(2):
  offset=slot*SLOT_BYTES;header=data[offset:offset+512]
  if len(header)!=512:continue
  magic,version,length,crc,_,generation,hcrc=struct.unpack_from('<8sIIIIQI',header)
  if magic!=b'AIONFS1\0' or version!=1 or length!=NODE.size*64:continue
  if zlib.crc32(header[:32])!=hcrc:continue
  payload=data[offset+512:offset+512+length]
  if len(payload)==length and zlib.crc32(payload)==crc:valid.append((generation,slot,payload))
 return sorted(valid,reverse=True)

def files(path):
 valid=snapshots(path)
 if not valid:raise ValueError('No valid AionOS snapshot')
 generation,slot,payload=valid[0];nodes=[]
 for i in range(64):
  used,directory,parent,size,identity,name,text=NODE.unpack_from(payload,i*NODE.size)
  nodes.append(dict(used=used,dir=directory,parent=parent,name=name.split(b'\0')[0].decode('ascii'),text=text[:size].decode('ascii'),identity=identity))
 def pathname(index,seen=None):
  if index==0:return ''
  seen=set() if seen is None else seen
  if index in seen or not 0<=index<64:raise ValueError('Invalid directory tree')
  seen.add(index);n=nodes[index];return pathname(n['parent'],seen)+'/'+n['name']
 result={pathname(i) or '/':n for i,n in enumerate(nodes) if n['used']}
 return result
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('image',nargs='?',default='data/aion-disk.img');p.add_argument('--cat');args=p.parse_args();entries=files(args.image)
 if args.cat:print(entries[args.cat]['text'],end='')
 else:
  for path,n in entries.items():print(path+('/' if n['dir'] and path!='/' else ''))
