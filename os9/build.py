#!/usr/bin/env python3
"""Build native LLVM OS-9 entries from the shared CMOC/C3 assembly bodies.

Only argument placement, result placement, symbol spelling and assembler
syntax change. No generated entry calls a foreign calling convention.
"""
import argparse
import json
import hashlib
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'c3'))
from native_asm import lower, parse, cfg, DIRECTIVES
from native_sources import interfaces
from profiles import select
from split_code import split

UNITS = ('io', 'process', 'mod', 'os_gs_ss', 'attr', 'id', 'time',
         'sleep', 'stat', 'syscall', 'syscommon', 'os9raw')
HELPERS = {'_osret', '_osok', '_oserr', '_os9err', '_sysret'}


def run(args, **kw):
    return subprocess.check_output([str(x) for x in args], **kw)


def select_llvm_inputs(text):
    """Remove the intermediate D move when the entry can consume X directly."""
    lines = text.splitlines()
    for i, raw in enumerate(lines):
        if raw != '\ttfr x,d /* native LLVM first argument */':
            continue
        for j in range(i + 1, len(lines)):
            x = parse(lines[j].split('/*', 1)[0])
            if x.op == 'tfr' and x.operand in ('d,x', 'd,y', 'd,u'):
                target = x.operand[-1]
                lines[i] = ''
                lines[j] = '' if target == 'x' else '\ttfr x,' + target
                if j + 1 < len(lines) and lines[j + 1].strip() == 'cmpd #0':
                    lines[j + 1] = '\tcmpx #0'
                break
            if x.op in ('pshs', 'leas', 'leau', 'leay', 'ldy', 'ldu'):
                if re.search(r'\b[abd]\b', x.operand):
                    break
                continue
            if x.op == 'tfr' and x.operand == 'u,y':
                continue
            break
    return '\n'.join(lines) + '\n'


def generate(source, name):
    api = interfaces()
    specs = {'_' + n: s for n, s in api.items() if n.startswith(('_os', 'n9_'))}
    # Non-OS C entry points in these units belong to their normal library.
    lines = []
    for raw in source.splitlines():
        x = parse(raw)
        if x.op == 'export' and x.label not in specs and x.label not in HELPERS | {'_getpid'}:
            continue
        lines.append(raw)
    pieces = split('\n'.join(lines) + '\n')
    result = []
    for piece in pieces:
        piece, report = lower(piece, {} if name == 'stat' else specs, name=name)
        piece = select(piece, name)
        lines = [parse(x) for x in piece.splitlines()]
        labels = {x.label: i for i, x in enumerate(lines) if x.label and x.op not in DIRECTIVES}
        entries = {s: i for s, i in labels.items() if s in specs or s in HELPERS}
        exits = set()
        arguments = set()
        for symbol, start in entries.items():
            exits.update(cfg(start, lines, labels, {}))
            if symbol in specs and specs[symbol]['args'] not in ('', 'void'):
                j = start + 1
                while j < len(lines) and (not lines[j].op or lines[j].op in DIRECTIVES):
                    j += 1
                arguments.add(j)
        exports = [x.label or x.operand for x in lines if x.op == 'export']
        mapping = {s: s[1:] for s in specs}
        mapping.update({s: '__n9' + s for s in HELPERS | {'_getpid'}})
        mapping.update({'_errno': 'errno'})
        output = ['/* Generated from lib/' + name + '.as; do not edit. */', '.text']
        for i, x in enumerate(lines):
            if i in arguments:
                output.append('\ttfr x,d /* native LLVM first argument */')
            if x.op == 'rts' and i in exits:
                output.append('\ttfr d,x /* native LLVM result */')
            if x.op == 'puls' and 'pc' in x.operand.split(',') and i in exits:
                regs = [r for r in x.operand.split(',') if r != 'pc']
                if regs:
                    output.append('\tpuls ' + ','.join(regs))
                output.extend(('\ttfr d,x', '\trts'))
                continue
            if name == 'process' and x.op == 'leau' and x.operand == ',s':
                output.append('\ttfr u,y /* process data base before F$Chain */')
            operand = x.operand
            operand = re.sub(r'\$([0-9a-fA-F]+)', r'0x\1', operand)
            if x.op == 'std' and operand.startswith('_errno'):
                output.append('\tleax mc6809_os9_data(errno),u')
                operand = ',x'
            if x.op == 'equ':
                output.append('.equ ' + x.label + ', ' + operand)
                continue
            if x.op in ('export', 'external', 'extern'):
                output.append(('.globl ' if x.op == 'export' else '.extern ') + (x.label or operand))
                continue
            if x.op in ('section', 'endsect', 'endsection', 'use'):
                continue
            if x.label:
                output.append(x.label + ':')
            if x.op:
                output.append('\t' + x.op + ' ' + operand)
        text = '\n'.join(output) + '\n'
        text = re.sub(r'\b[A-Za-z_]\w*\b', lambda m: mapping.get(m[0], m[0]), text)
        text = re.sub(r'\ttfr x,d /\* native LLVM first argument \*/\n\tpshs d((?:,[a-z]+)*)\n', r'\tpshs x\1\n', text)
        text = select_llvm_inputs(text)
        text = text.replace('\tclra \n\tclrb \n\ttfr d,x /* native LLVM result */', '\tldx #0')
        # Public compatibility names are aliases of the same native entry.
        for symbol in exports:
            if symbol in specs and symbol.startswith('__os'):
                public = mapping[symbol]
                text += '.globl cmoc' + public + '\n.set cmoc' + public + ', ' + public + '\n'
        compatibility = {'n9_seek': '__os9_seek', 'n9_getstt_xu': '__os9_getstt_xu', 'n9_setstt_xu': '__os9_setstt_xu', 'n9_link': '__os9_link', 'n9_load': '__os9_load', 'n9_unlink': '__os9_unlink'}
        for public, alias in compatibility.items():
            if '_' + public in exports:
                text += '.globl ' + alias + '\n.set ' + alias + ', ' + public + '\n'
        result.append(text)
    return result


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--clang', required=True, type=Path)
    p.add_argument('--ar', required=True, type=Path)
    p.add_argument('--lwasm', default='lwasm')
    p.add_argument('--out', required=True, type=Path)
    p.add_argument('--archive', type=Path)
    p.add_argument('--revision')
    p.add_argument('--extra-object', type=Path, action='append', default=[])
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    objects = []
    for name in UNITS:
        raw = run([a.lwasm, '-DNITROS9_LLVM=1', '-P', ROOT / 'lib' / (name + '.as')]).decode()
        for i, text in enumerate(generate(raw, name)):
            source = a.out / (name + '_' + str(i) + '.S')
            source.write_text(text)
            obj = source.with_suffix('.o')
            run([a.clang, '--target=mc6809-unknown-os9', '-c', source, '-o', obj])
            objects.append(obj)
    archive = a.archive or a.out / 'libnitros9_os.a'
    archive.parent.mkdir(parents=True, exist_ok=True)
    archive.unlink(missing_ok=True)
    run([a.ar, 'rcs', archive, *objects, *a.extra_object])
    sources = [ROOT / 'lib' / (n + '.as') for n in UNITS]
    sources += [ROOT / 'os9/build.py', ROOT / 'os9/include/os9.h']
    sources += sorted((ROOT / 'include').glob('*.h'))
    sources += sorted((ROOT / 'include').glob('*.d'))
    sources += [ROOT / 'c3' / n for n in ('native_asm.py', 'native_sources.py', 'profiles.py', 'split_code.py')]
    manifest = {'abi': 'LLVM MC6809: first word/pointer and int result in X; U data base',
                'revision': a.revision,
                'source_sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (a.out / 'sources.json').write_text(json.dumps(manifest, indent=2) + '\n')


if __name__ == '__main__':
    main()
