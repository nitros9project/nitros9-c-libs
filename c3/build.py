#!/usr/bin/env python3
"""Compile the canonical library sources with C3 and assemble its native ABI."""
import argparse
import json
import hashlib
from pathlib import Path
import re
import subprocess

from native_sources import c_view, interfaces, write_headers
from native_asm import lower
from private_stdio import select as select_private_stdio
from split_code import split as split_code
from profiles import select as select_profile
from native_calls import lower as lower_calls
from long_returns import select as select_long_returns

ROOT = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    result = subprocess.run([str(x) for x in command], capture_output=True, timeout=30, **kwargs)
    if result.returncode:
        raise RuntimeError(' '.join(map(str, command))+'\n'+result.stderr.decode(errors='replace')+result.stdout.decode(errors='replace')[-1500:])
    return result.stdout


def adapt_data(text, name, backend):
    # C3 addresses C data through Y, including const tables. Its CRT installs
    # initialized data images and relocates pointers into the per-process area.
    readonly=re.findall(r'^\s*section\s+rodata[^\n]*\n(.*?)^\s*endsect(?:ion)?',text,re.I|re.M|re.S)
    rolabels=set()
    for body in readonly:
        rolabels.update(re.findall(r'^([A-Za-z_]\w*)',body,re.M))
    for label in rolabels:
        text=re.sub(r'\b'+re.escape(label)+r'([^,\n]*),pcr\b',label+r'\1,y',text,flags=re.I)
    text=re.sub(r'(?im)^(\s*section\s+)rodata\b',r'\1rwdata',text)
    pattern = re.compile(r'^\s*section\s+rwdata[^\n]*\n(.*?)^\s*endsect(?:ion)?[^\n]*(?:\n|$)', re.I | re.M | re.S)
    public = set(re.findall(r'^\s*([.\w]+)\s+EXPORT\b', text, re.I | re.M))
    public.update(re.findall(r'^\s*EXPORT\s+([.\w]+)', text, re.I | re.M))
    data_index=0
    def replace(match):
        nonlocal data_index
        data_index+=1
        body = re.sub(r'^([.\w]+)\s+EQU\s+\*.*$',r'\1',match[1],flags=re.I|re.M)
        body = '\n'.join(line.split(';',1)[0].rstrip() if not re.search(r'\bfcc\b',line,re.I) else line for line in body.splitlines())
        body = re.sub(r'(?im)^.*\b(?:EXPORT|EXTERNAL|EXTERN)\b.*$', '', body)
        body = re.sub(r'(?i)\b(FCB|FDB|FCC|FQB|RMB|RZB|EQU|SET)\b',lambda m:m[0].lower(),body)
        rma = ' psect c3_data_'+name+'_'+str(data_index)+',0,0,0,0,0\n vsect\n'+body+'\n endsect\n endsect\n'
        result = run(['awk','-f',backend/'c3lw.awk'],input=rma.encode()).decode()
        return '\n'.join(line for line in result.splitlines() if not line.startswith('\texport\t') or line.split()[-1] in public)+'\n'
    return pattern.sub(replace,text)



def optimize_rma(rma, name, optimizer):
    # optx merges adjacent vsects, turning BSS into initialized zero images.
    # A data-only unit has no instructions to optimize.
    if not re.search(rb'(?m)^\s+ttl\s+',rma):return rma
    if name=='ctypefn':
        # Whole-unit tail merging makes otherwise independent APIs inseparable
        # in the archive. Optimize each data-free leaf function in isolation.
        if re.search(rb'(?m)^\s+vsect',rma):raise ValueError('ctypefn gained shared data')
        pieces=re.split(rb'(?m)(?=^[ \t]+ttl[ \t]+)',rma)
        prefix=pieces[0]
        return b'\n'.join(run([optimizer],input=prefix+piece.removesuffix(b' endsect\n')+b' endsect\n') for piece in pieces[1:])
    return run([optimizer],input=rma)


def inline_assembly(text):
    """Extract CMOC's verbatim asm bodies; compile ordinary C with C3."""
    blocks=[]
    pattern=re.compile(r'(?:__norts__\s+asm|asm\s+__norts__)\s+(?:int|void)\s+(\w+)\([^{}]*\)\s*\{\s*asm\s*\{(.*?)\}\s*\}',re.S)
    def extract(match):
        blocks.append(' section code\n_'+match[1]+' EXPORT\n_'+match[1]+':\n'+match[2]+'\n endsection\n')
        return ''
    text=pattern.sub(extract,text)
    return text,'\n'.join(blocks)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--c3',type=Path,required=True,help='built nitros9-languages/c3 tree')
    parser.add_argument('--out',type=Path,default=ROOT/'c3/out')
    args=parser.parse_args()
    c3=args.c3.resolve();out=args.out.resolve();out.mkdir(parents=True,exist_ok=True)
    backend=c3/'lwbackend'
    aliases=write_headers(out/'include')
    specs={'_'+name:spec for name,spec in interfaces().items()}
    makefile=out/'list.mk';makefile.write_text('listmods:\n\t@echo $(BASE_MODS)\n')
    modules=run(['make','-s','-C',ROOT/'lib','-f','Makefile','-f',makefile,'listmods']).decode().split()
    objects=[];reports={};assembly={};globals=set()
    for entry in modules:
        name=Path(entry).stem
        if name in ('case','fcommon','rpterr'):continue
        source=next(ROOT/'lib'/(name+suffix) for suffix in ('.c','.as','.asm') if (ROOT/'lib'/(name+suffix)).exists())
        if source.suffix=='.c':
            content=source.read_text()
            content,asm=inline_assembly(content)
            content=c_view(content,aliases=aliases)
            content=content.replace('char s[]="test";','static char s[]="test";')
            unit=out/(name+'.c');unit.write_text(content)
            preprocessed=run([c3/'build/unix/prep/c3prep','-DOS9','-DNITROS9_C3','-v='+str(out/'include'),unit.name],cwd=out)
            if b'****' in preprocessed:raise RuntimeError(preprocessed.decode(errors='replace'))
            rma=run([c3/'build/unix/comp/c3comp','-s'],input=preprocessed)
            if b'****' in rma:raise RuntimeError(rma.decode(errors='replace'))
            (out/(name+'.rma')).write_bytes(rma)
            globals.update(re.findall(r'(?m)^([A-Za-z_]\w*):',rma.decode()))
            rma=optimize_rma(rma,name,c3/'build/unix/optx/c3optx')
            native=run(['awk','-f',backend/'c3lw.awk'],input=rma).decode()
            if asm:
                defines='\n'.join(line for line in source.read_text().splitlines() if line.startswith(('#if','#else','#endif','#define')))
                # printf defines its ABI constants above the C includes.
                prefix=source.read_text().split('#include',1)[0] if name=='printf' else ''
                asm=run(['cpp','-P','-DNITROS9_C3','-'],input=(prefix+'\n'+asm).encode()).decode()
            assembly[name]=(native,asm)
        else:
            assembly[name]=('',run(['lwasm','-DNITROS9_C3=1','-P',source]).decode())
    readonly_labels=set()
    for _,asm in assembly.values():
        for body in re.findall(r'^\s*section\s+rodata[^\n]*\n(.*?)^\s*endsect(?:ion)?',asm,re.I|re.M|re.S):
            readonly_labels.update(re.findall(r'^([A-Za-z_]\w*)',body,re.M))
    symbols={'_'+name:aliases.get(name,name[:8]) for name in interfaces()}
    symbols.update({'_'+name:name for name in globals})
    symbols.update({'__memend':'memend','__mtop':'_mtop','__stbot':'_stbot','_errno':'errno'})
    for name,(native,asm) in assembly.items():
        if asm:
            for label in readonly_labels:
                asm=re.sub(r'\b'+re.escape(label)+r'([^,\n]*),pcr\b',label+r'\1,y',asm,flags=re.I)
            explicit=name in ('utime','ltoa','dirseek','bsearch','create')
            if not explicit:asm=select_long_returns(asm,name)
            asm,report=lower(asm,{} if explicit or name in ('cfinish','printf','debug','stat') else {k:v for k,v in specs.items() if not (name=='fseek' and k in ('_fseek','_rewind'))},name=name)
            asm=select_profile(asm,name)
            asm=select_private_stdio(asm,name)
            call_specs=dict(specs)
            call_specs.update({name:specs['_'+name] for name in ('toupper','tolower')})
            if explicit:calls=[]
            else:asm,calls=lower_calls(asm,call_specs,name)
            reports[name]={'entries':report,'calls':calls}
            asm=re.sub(r'\b[A-Za-z_]\w*\b',lambda m:symbols.get(m[0],m[0]),asm)
            # Collapse legacy assembly aliases that become the same native symbol.
            seen=set();clean=[]
            for line in asm.splitlines():
                match=re.match(r'^([A-Za-z_]\w*):\s*$',line)
                if match and match[1] in seen: continue
                if match: seen.add(match[1])
                clean.append(line)
            asm=adapt_data('\n'.join(clean)+'\n',name,backend)
        text=native+'\n'+asm
        text=re.sub(r'(?m)^[ \t]*leas[ \t]+\(([0-9]+)\)-([0-9]+),s[^\n]*$',lambda m:'' if m[1]==m[2] else m[0],text)
        (out/(name+'.s')).write_text(text)
        pieces=split_code(text) if name in ('io','ctypefn','stat','syscommon') else [text]
        for index,piece in enumerate(pieces):
            stem=name+('_'+str(index) if len(pieces)>1 else '')
            target=out/(stem+'.s');target.write_text(piece)
            obj=out/(stem+'.o')
            run(['lwasm','--format=obj','-o',obj,target],cwd=out)
            objects.append(obj)
    archive=out/'libc3.a';archive.unlink(missing_ok=True)
    run(['lwar','-c',archive,*objects])
    metadata={'compiler_stages':{name:hashlib.sha256((c3/'build/unix'/folder/name).read_bytes()).hexdigest() for folder,name in [('prep','c3prep'),('comp','c3comp'),('optx','c3optx')]},'sources':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'lib').iterdir()) if p.suffix in ('.c','.as','.asm')},'library_sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'source_units':len(assembly),'archive_members':len(objects)}
    (out/'BUILD.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (out/'abi-report.json').write_text(json.dumps(reports,indent=2)+'\n')
    print('Built',archive,'with',len(objects),'archive members from',len(assembly),'canonical source units using native C3')


if __name__=='__main__':main()
