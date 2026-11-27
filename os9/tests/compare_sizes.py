#!/usr/bin/env python3
from pathlib import Path
import subprocess,shutil,json,hashlib
import argparse
p=argparse.ArgumentParser(description="Compare LLVM OS-9 module sizes with prepared bakeoff app sources")
p.add_argument('--prepared',type=Path,required=True)
p.add_argument('--old-clang',type=Path,required=True)
p.add_argument('--shared-clang',type=Path,required=True)
p.add_argument('--old-sysroot',type=Path,required=True)
p.add_argument('--shared-sysroot',type=Path,required=True)
p.add_argument('--out',type=Path,required=True)
a=p.parse_args()
source=a.prepared.resolve()
configs=[('old',a.old_clang.resolve(),a.old_sysroot.resolve()),('shared',a.shared_clang.resolve(),a.shared_sysroot.resolve())]
a.out=a.out.resolve()
rows=[]
for opt in ['s','z','2']:
 for app in ['uniq','dgrep','ed','cb','lb','ppc','uemacs']:
  row={'application':app,'optimization':'-O'+opt}
  for label,cc,sysroot in configs:
   out=a.out/('O'+opt)/app/label
   out.mkdir(parents=True,exist_ok=True)
   for f in (source/app).iterdir():
    if f.suffix in ['.c','.h']:shutil.copyfile(f,out/f.name)
   sources=sorted(p.name for p in out.glob('*.c') if app!='uemacs' or p.name not in ('uetermio.c','uecoco.c','uevt52.c','uetcap.c'))
   cmd=[str(cc),'--target=mc6809-unknown-os9','--sysroot='+str(sysroot),'-mcpu=mc6809','-std=gnu89','-Wno-implicit-int','-Wno-implicit-function-declaration','-Wno-deprecated-non-prototype','-O'+opt,'-Wl,-Map=appmod.map',*sources,'-o','appmod']
   with (out/'build.log').open('wb') as log:r=subprocess.run(cmd,cwd=out,stdout=log,stderr=subprocess.STDOUT)
   if r.returncode:raise RuntimeError(str(out)+'\n'+(out/'build.log').read_text()[-3000:])
   row[label]=(out/'appmod').stat().st_size
  row['delta']=row['shared']-row['old'];rows.append(row);print(row,flush=True)
(a.out/'results.json').write_text(json.dumps(rows,indent=2)+'\n')
manifest={'compiler_versions':{label:subprocess.check_output([cc,'--version']).decode() for label,cc,sysroot in configs},'prepared_sha256':{str(p.relative_to(source)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source.rglob('*')) if p.suffix in ('.c','.h')},'arguments':{k:str(v) for k,v in vars(a).items()}}
(a.out/'inputs.json').write_text(json.dumps(manifest,indent=2)+'\n')
