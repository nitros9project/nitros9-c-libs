#!/usr/bin/env python3
"""Build and execute the same OS-call contracts for CMOC, C3 and LLVM."""
import argparse
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]


def run(args, log, **kwargs):
    with log.open('wb') as output:
        result = subprocess.run([str(x) for x in args], stdout=output, stderr=subprocess.STDOUT, **kwargs)
    if result.returncode:
        raise RuntimeError(str(args) + '\n' + log.read_text(errors='replace')[-4000:])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--llvm-bin', type=Path, required=True)
    p.add_argument('--sysroot', type=Path, required=True)
    p.add_argument('--c3', type=Path, required=True)
    p.add_argument('--cmoc', default='cmoc')
    p.add_argument('--lwasm', type=Path, required=True)
    p.add_argument('--boot-disk', type=Path, required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--os9', default='os9')
    p.add_argument('--emulator', default='usim09pt')
    p.add_argument('--out', type=Path, default=ROOT / 'os9/out/check')
    a = p.parse_args()
    a.out = a.out.resolve()
    a.out.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env['PATH'] = str(a.lwasm.resolve().parent) + os.pathsep + env['PATH']
    python = sys.executable
    c3out = a.out / 'c3'
    run([python, ROOT / 'c3/build.py', '--c3', a.c3.resolve(), '--out', c3out], a.out / 'c3-build.log', env=env)
    run(['make', '-C', ROOT / 'lib', '-j4'], a.out / 'cmoc-build.log', env=env)
    run(['make', '-C', ROOT / 'llvm', '-j4', 'LLVM_BIN=' + str(a.llvm_bin.resolve()), 'OS9_SYSROOT=' + str(a.sysroot.resolve()), 'LWASM=' + str(a.lwasm.resolve())], a.out / 'llvm-build.log', env=env)
    run([a.cmoc, '--os9', '-nodefaultlibs', '--cpp=cpp -Wno-builtin-macro-redefined', '-I' + str(ROOT / 'include'), '--add-os9-stack-space=2048', '-O2', '-on9cmoc', ROOT / 'os9/tests/portable_kernel.c', '-L' + str(ROOT / 'lib'), '-lc'], a.out / 'cmoc-compile.log', cwd=a.out, env=env)
    sys.path.insert(0, str(ROOT / 'c3'))
    from native_sources import c_view
    from runtime import stage
    runtime = stage(a.c3.resolve(), c3out / 'libc3.a', c3out / 'runtime')
    c3env = dict(env, LC_ALL='C', C3BASE=str(a.c3.resolve()), C3LW_HOME=str(runtime))
    c3env['PATH'] = os.pathsep.join(str(a.c3.resolve() / 'build/unix' / x) for x in ('exec', 'prep', 'comp', 'optx')) + os.pathsep + str(runtime) + os.pathsep + env['PATH']
    (a.out / 'portable.c').write_text(c_view((ROOT / 'os9/tests/portable_kernel.c').read_text()))
    run(['c3', '-y', '-q', '-v=' + str(c3out / 'include'), 'portable.c', '-f=n9c3'], a.out / 'c3-compile.log', cwd=a.out, env=c3env)
    clang = a.llvm_bin.resolve() / 'clang'
    common = [clang, '--target=mc6809-unknown-os9', '--sysroot=' + str(a.sysroot.resolve()), '-Os', '-I' + str(ROOT / 'llvm/include')]
    library = ROOT / 'llvm/out/Os/libcmoc_os9_compat.a'
    (a.out / 'child.c').write_text('int main(void) { return 7; }\n')
    for name, source in [('n9llvm', ROOT / 'os9/tests/portable_kernel.c'), ('n9chain', ROOT / 'os9/tests/chain_child.c'), ('n9kid', a.out / 'child.c')]:
        run(common + [source, library, '-o', a.out / name], a.out / (name + '-compile.log'), env=env)
    command = [python, ROOT / 'os9/tests/run_kernel.py', '--boot-disk', a.boot_disk.resolve(), '--firmware', a.firmware.resolve(), '--os9', a.os9, '--emulator', a.emulator, '--out', a.out / 'kernel']
    for name in ('n9cmoc', 'n9c3', 'n9llvm'):
        command += ['--program', a.out / name]
    for name in ('n9kid', 'n9chain'):
        command += ['--asset', a.out / name]
    run(command, a.out / 'kernel.log', env=env)
    print((a.out / 'kernel.log').read_text())


if __name__ == '__main__':
    main()
