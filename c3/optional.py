"""Build optional native C3 archives from the canonical source directories."""
from pathlib import Path
import re
from native_sources import c_view
from rma_sources import prepare, assembly

CGFX_ORDER = '''getwind setwind cbuffer polyline polyfill polyfunc dialog mousekey
settype sinecosine button tandy object mvmenu mvmenuxy mvfname getstr fname menu
menuxy shadow text getput play window config font radio draw status mouse alarm
mv_window keysense sound crw mousexy drawfunc nobuffer'''.split()


def build(root, c3, out, aliases, run, optimize, adapt):
    variants={}
    (out/'include/ttydefs.h').write_text(c_view((root/'termcap/ttydefs.h').read_text(),header=True,aliases=aliases))
    def compile_c(source, name):
        unit=out/(name+'.c');unit.write_text(c_view(source.read_text(),aliases=aliases))
        prep=run([c3/'build/unix/prep/c3prep','-DOS9','-DNITROS9_C3','-v='+str(out/'include'),unit.name],cwd=out)
        if b'****' in prep:raise RuntimeError(prep.decode())
        rma=run([c3/'build/unix/comp/c3comp','-s'],input=prep)
        if b'****' in rma:raise RuntimeError(rma.decode())
        rma=optimize(rma,name,c3/'build/unix/optx/c3optx')
        return run(['awk','-f',c3/'lwbackend/c3lw.awk'],input=rma).decode('latin1')
    def archive(name, sources):
        objects=[]
        for source in sources:
            stem=name+'_'+source.stem
            text=source.read_text(encoding='latin1')
            match=re.search(r'\* C3_RMA_BEGIN\n(.*?)\* C3_RMA_END',text,re.S)
            if match:
                body=re.sub(r'^\s*(?:ifp1|endc)\b[^\n]*','',match[1],flags=re.M|re.I)
                body=re.sub(r'\b[A-Za-z_]\w*\b',lambda m:aliases.get(m[0],m[0]),body)
                native=prepare(body,c3)
            elif source.suffix=='.c':native=compile_c(source,stem)
            else:native=assembly(source,c3)
            # Keep high-bit graphics bytes independent of the host encoding.
            def byte_string(match):
                data=match[3]
                if not any(ord(c)>127 for c in data):return match[0]
                return match[1]+'fcb '+','.join(str(ord(c)) for c in data)
            native=re.sub(r'(?m)^([^\n]*?\b)fcc[ \t]+(["/])(.*?)\2[ \t]*$',byte_string,native)
            native=adapt(native,stem,c3/'lwbackend')
            target=out/(stem+'.s');target.write_bytes(native.encode('latin1'))
            obj=out/(stem+'.o');run(['lwasm','--format=obj','--pragma=undefextern','-o',obj,target],cwd=out);objects.append(obj)
        target=out/(name+'.a');target.unlink(missing_ok=True)
        run(['lwar','-c',target,*objects]);variants[target.name]=objects
    archive('libcgfx', [next(root/'cgfx'/(name+suffix) for suffix in ('.c','.as') if (root/'cgfx'/(name+suffix)).exists()) for name in CGFX_ORDER])
    archive('libtermcap',[root/'termcap'/(name+'.c') for name in ('crtbynam','crtbypth','tparam')])
    archive('libalib',[source for source in sorted((root/'asm').glob('*.a')) if source.stem!='test'])
    archive('libdbg',[root/'lib/dbglib.c'])
    return variants
