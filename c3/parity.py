#!/usr/bin/env python3
"""Check migrated C3 features at both optimization levels on an OS-9 kernel."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import time

from build import ROOT, run
from native_sources import c_view
from runtime import stage


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--c3',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=ROOT/'c3/out')
    parser.add_argument('--boot-disk',type=Path,help='Pico-Thing boot image using /dd startup')
    parser.add_argument('--firmware',type=Path)
    parser.add_argument('--fpo9',type=Path,help='MC6839 FPO9 module, required for kernel execution')
    parser.add_argument('--emulator',default='usim09pt')
    parser.add_argument('--os9',default='os9')
    parser.add_argument('--wall-seconds',type=int,default=60)
    args=parser.parse_args()
    out=args.out.resolve();c3=args.c3.resolve();work=out/'parity';work.mkdir(parents=True,exist_ok=True)
    runtime=stage(c3,out/'libc3.a',out/'runtime')
    env=os.environ.copy();env.update(C3BASE=str(c3),C3LW_HOME=str(runtime))
    env['PATH']=os.pathsep.join(str(c3/'build/unix'/part) for part in ('exec','prep','comp','optx'))+os.pathsep+str(runtime)+os.pathsep+env['PATH']
    tests = {
        'scanf': ('fp.l','SCAN'), 'float': ('clibf.l','FLOAT'),
        'math': ('fp.l','MATH'), 'cgfx': ('cgfx.l','CGFX'),
        'alib': ('alib.l','ALIB'), 'termcap': ('termcap.l','TERMCAP'),
        'env': ('','ENV'), 'system': ('','SYSTEM'), 'debug': ('dbg.l','DEBUG'),
    }
    programs=[]
    for test,(library,marker) in tests.items():
      source='parity-'+test+'.c'
      (work/source).write_text(c_view((ROOT/'c3/tests'/source).read_text()))
      for optimization in (0,2):
        name='p'+test[:5]+str(optimization)
        command=['c3','-y','-q','-v='+str(out/'include'),source,'-f='+name]
        if library:command.append('-l='+library)
        if not optimization:command.append('-o')
        run(command,cwd=work,env=env)
        program=work/name
        programs.append({'name':name,'feature':test,'expected':marker+' PASS\r',
                         'optimizer':optimization,'module_bytes':program.stat().st_size,
                         'sha256':hashlib.sha256(program.read_bytes()).hexdigest(),'command':command})
    report={'library_sha256':hashlib.sha256((out/'libc3.a').read_bytes()).hexdigest(),'programs':programs}
    if args.boot_disk:
        if not args.firmware or not args.fpo9:parser.error('--firmware and --fpo9 are required with --boot-disk')
        disk=work/'test.dsk';shutil.copyfile(args.boot_disk,disk)
        disk_arg=lambda name:str(disk)+','+name
        run([args.os9,'copy','-r',args.fpo9,disk_arg('Modules/FPO9')])
        for folder in ('C3TEST','C3TEST/CMDS'):run([args.os9,'makdir',disk_arg(folder)])
        startup=['chx /dd/c3test/cmds','chd /dd/c3test','echo C3TESTBEGIN']
        for program in programs:
            name=program['name']
            run([args.os9,'copy','-r',work/name,disk_arg('C3TEST/CMDS/'+name)])
            run([args.os9,'attr','-q','-e','-pe','-pr',disk_arg('C3TEST/CMDS/'+name)])
            startup.extend(['echo '+name,name+' >'+name+'.out >>'+name+'.err'])
        startup.append('echo C3TESTDONE')
        (work/'startup').write_bytes(('\r'.join(startup)+'\r').encode())
        run([args.os9,'copy','-r',work/'startup',disk_arg('startup')])
        run([args.os9,'attr','-q','-npe','-npw','-pr','-ne','-w','-r',disk_arg('startup')])
        (work/'state.fram').unlink(missing_ok=True)
        console=work/'console.log';complete=False
        with console.open('wb') as log:
            process=subprocess.Popen([args.emulator,'--timeout=3000000000','-f',str(work/'state.fram'),'-d',str(disk),str(args.firmware.resolve())],cwd=work,stdin=subprocess.DEVNULL,stdout=log,stderr=subprocess.STDOUT)
            deadline=time.monotonic()+args.wall_seconds
            try:
                while process.poll() is None and time.monotonic()<deadline:
                    if b'C3TESTDONE\n' in console.read_bytes().replace(b'\r',b''):
                        complete=True;break
                    time.sleep(.2)
            finally:
                if process.poll() is None:process.terminate()
                process.wait(timeout=10)
        report['completed']=complete
        for program in programs:
            name=program['name'];actual={}
            for extension in ('out','err'):
                target=work/(name+'.'+extension);target.unlink(missing_ok=True)
                run([args.os9,'copy','-r',disk_arg('C3TEST/'+target.name),target])
                actual[extension]=target.read_bytes().decode('ascii',errors='replace')
            program['output']=actual
            program['status']='PASS' if complete and actual=={'out':program['expected'],'err':''} else 'FAIL'
        report['console']=console.read_text(errors='replace')
    (work/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    for program in programs:print(program['name'],program.get('status','BUILT'),program['module_bytes'])
    if args.boot_disk and not all(p['status']=='PASS' for p in programs):raise SystemExit(1)


if __name__=='__main__':main()
