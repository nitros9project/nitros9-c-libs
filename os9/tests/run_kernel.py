#!/usr/bin/env python3
"""Run compiler-native probes together on a real NitrOS-9 kernel."""
import argparse
from pathlib import Path
import shutil
import subprocess
import time


def run(args):
    return subprocess.check_output([str(x) for x in args], stderr=subprocess.STDOUT)


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--boot-disk', type=Path, required=True)
    p.add_argument('--firmware', type=Path, required=True)
    p.add_argument('--os9', default='os9')
    p.add_argument('--emulator', default='usim09pt')
    p.add_argument('--out', type=Path, required=True)
    p.add_argument('--program', type=Path, action='append', required=True)
    p.add_argument('--asset', type=Path, action='append', default=[])
    p.add_argument('--wall-seconds', type=int, default=90)
    a = p.parse_args()
    a.out.mkdir(parents=True, exist_ok=True)
    disk = a.out / 'kernel.dsk'
    shutil.copy2(a.boot_disk, disk)
    for name in ('N9CALLS', 'N9CALLS/CMDS'):
        run([a.os9, 'makdir', str(disk) + ',' + name])
    names = []
    for source in a.program + a.asset:
        name = run([a.os9, 'ident', '-s', source]).decode().split()[-1]
        run([a.os9, 'copy', '-r', source, str(disk) + ',N9CALLS/CMDS/' + name])
        run([a.os9, 'attr', '-q', '-e', '-pe', '-pr', str(disk) + ',N9CALLS/CMDS/' + name])
        if source in a.program:
            names.append(name)
    startup = ['chx /dd/n9calls/cmds', 'chd /dd/n9calls', 'echo N9BEGIN']
    for name in names:
        startup += ['echo ' + name, name + ' >' + name + '.out >>' + name + '.err']
    startup.append('echo N9DONE')
    (a.out / 'startup').write_bytes(('\r'.join(startup) + '\r').encode())
    run([a.os9, 'copy', '-r', a.out / 'startup', str(disk) + ',startup'])
    run([a.os9, 'attr', '-q', '-npe', '-npw', '-pr', '-ne', '-w', '-r', str(disk) + ',startup'])
    (a.out / 'state.fram').unlink(missing_ok=True)
    console = a.out / 'console.log'
    with console.open('wb') as log:
        proc = subprocess.Popen([a.emulator, '--timeout=3000000000', '-f', str(a.out / 'state.fram'), '-d', str(disk), str(a.firmware)], stdout=log, stderr=subprocess.STDOUT)
        try:
            end = time.monotonic() + a.wall_seconds
            while proc.poll() is None and time.monotonic() < end:
                if b'N9DONE' in console.read_bytes():
                    break
                time.sleep(.1)
        finally:
            if proc.poll() is None:
                proc.terminate()
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
    if b'N9DONE' not in console.read_bytes():
        raise SystemExit('kernel did not finish: ' + str(console))
    failed = []
    for name in names:
        output = a.out / (name + '.out')
        run([a.os9, 'copy', '-r', str(disk) + ',N9CALLS/' + name + '.out', output])
        data = output.read_bytes()
        passed = b'N9 OS CALLS PASS' in data and b'FAIL' not in data
        print(name, 'PASS' if passed else 'FAIL', repr(data[-300:]), flush=True)
        if not passed:
            failed.append(name)
    return bool(failed)


if __name__ == '__main__':
    raise SystemExit(main())
