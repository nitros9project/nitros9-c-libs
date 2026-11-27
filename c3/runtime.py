"""Stage compiler-owned startup and arithmetic primitives beside the library."""
from pathlib import Path
import shutil
from build import run


def stage(c3, archive, destination):
    c3=Path(c3).resolve();destination=Path(destination).resolve()
    destination.mkdir(parents=True,exist_ok=True)
    backend=c3/'lwbackend'
    for name in ('c3-as','c3-ld','c3lw.awk','os9c3.ld'):
        shutil.copy2(backend/name,destination/name)
    (destination/'crt0.s').write_text((backend/'crt0.s').read_text()+'\n export argv\n')
    run(['lwasm','--format=obj','-o',destination/'crt0.o',destination/'crt0.s'],cwd=destination)
    for name in ('fpwrap','fpdummy','fpinit'):
        source=run(['sed','-f',backend/'os9defs.sed',backend/(name+'.a')])
        assembly=run(['awk','-f',backend/'c3lw.awk'],input=source)
        target=destination/(name+'.s');target.write_bytes(assembly)
        run(['lwasm','--format=obj','-o',destination/(name+'.o'),target],cwd=destination)
    shutil.copy2(archive,destination/'libc3.a')
    for name in ('libc3f.a','libcgfx.a','libtermcap.a','libalib.a','libdbg.a'):
        source=Path(archive).parent/name
        if source.exists():shutil.copy2(source,destination/name)
    helpers=destination/'libc3lw.a';helpers.unlink(missing_ok=True)
    run(['lwar','-c',helpers,destination/'fpwrap.o'],cwd=destination)
    return destination
