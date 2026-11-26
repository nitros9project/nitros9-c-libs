#!/usr/bin/env python3
"""Account for every module byte using two C3 lwlink maps and their modules."""
import argparse
import hashlib
import json
from pathlib import Path
import re

LOADED = {'code', '.text', 'data', '.data', 'irec', 'ireloc', 'icreloc'}
RAM = {'directpage', 'bss', '.bss', 'stack'}
SECTION = re.compile(r'^Section: (\S+) \((.*)\) load at ([0-9A-Fa-f]+), length ([0-9A-Fa-f]+)$')


def measure(map_text, module):
    if module[:2] != b'\x87\xcd' or int.from_bytes(module[2:4], 'big') != len(module):
        raise ValueError('invalid OS-9 module header/length')
    name=[]
    for byte in module[int.from_bytes(module[4:6], 'big'):-3]:
        name.append(chr(byte & 127))
        if byte & 128:break
    else:raise ValueError('unterminated module name')
    members={}
    for line in map_text.splitlines():
        match=SECTION.fullmatch(line)
        if not match:continue
        section, path, _, length=match.groups();length=int(length,16)
        if length and section not in LOADED|RAM:raise ValueError('unknown section: '+section)
        sections=members.setdefault(Path(path).stem,{})
        sections[section]=sections.get(section,0)+length
    if not members:raise ValueError('no linker map sections')
    loaded={member:sum(size for section,size in sections.items() if section in LOADED)
            for member,sections in members.items()}
    loaded_bytes=sum(loaded.values());overhead=len(module)-loaded_bytes
    # OS-9 program header + high-bit-terminated name + CRC. RAM is not ROM.
    expected=13+len(name)+3
    if overhead != expected:raise ValueError(f'unaccounted bytes: expected {expected} header/name/CRC bytes, got {overhead}')
    return {'module_bytes':len(module),'module_name':''.join(name),
            'module_sha256':hashlib.sha256(module).hexdigest(),
            'loaded_bytes':loaded_bytes,'overhead_bytes':overhead,
            'members':members,'loaded_members':loaded}


def compare(old,new):
    rows=[{'member':name,'old':old['loaded_members'].get(name,0),
           'new':new['loaded_members'].get(name,0)}
          for name in sorted(old['members'].keys()|new['members'].keys())]
    for row in rows:row['delta']=row['new']-row['old']
    delta=new['module_bytes']-old['module_bytes']
    assert sum(row['delta'] for row in rows)+new['overhead_bytes']-old['overhead_bytes']==delta
    return {'old':old,'new':new,'delta':delta,'members':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    for side in ('old','new'):
        parser.add_argument('--'+side+'-map',type=Path,required=True)
        parser.add_argument('--'+side+'-module',type=Path,required=True)
    parser.add_argument('--json',type=Path)
    args=parser.parse_args()
    old=measure(args.old_map.read_text(),args.old_module.read_bytes())
    new=measure(args.new_map.read_text(),args.new_module.read_bytes())
    report=compare(old,new)
    if args.json:
        args.json.parent.mkdir(parents=True,exist_ok=True)
        args.json.write_text(json.dumps(report,indent=2)+'\n')
    print('Member | Old loaded bytes | New loaded bytes | Change')
    for row in report['members']:
        if row['delta']:print(f"{row['member']} | {row['old']} | {row['new']} | {row['delta']:+d}")
    print(f"Header/name/CRC | {old['overhead_bytes']} | {new['overhead_bytes']} | {new['overhead_bytes']-old['overhead_bytes']:+d}")
    print(f"Module | {old['module_bytes']} | {new['module_bytes']} | {report['delta']:+d}")


if __name__=='__main__':main()
