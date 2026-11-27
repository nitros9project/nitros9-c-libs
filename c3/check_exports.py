#!/usr/bin/env python3
"""Require every declared graphics API and migrated feature to link natively."""
import argparse
from pathlib import Path
import re
from build import ROOT,run
from native_sources import names,split_declarations
from runtime import stage


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--c3',type=Path,required=True)
    parser.add_argument('--out',type=Path,default=ROOT/'c3/out')
    args=parser.parse_args();out=args.out.resolve();work=out/'exports';work.mkdir(exist_ok=True)
    home=stage(args.c3,out/'libc3f.a',work/'runtime')
    text=split_declarations(re.sub(r'/\*.*?\*/','',(ROOT/'cgfx/include/cgfx.h').read_text(),flags=re.S))
    api=[name for ret,name,_ in re.findall(r'(?m)^([A-Za-z_][^\n;{}]*?)\b([A-Za-z_]\w*)\s*\(([^;{}]*?)\);',text,re.S) if not ret.strip().startswith('typedef')]
    api+='scanf fscanf sscanf atof scale pffinit sin cos atan asin acos tan sqrt sqr inv dexp fabs exp log log10 pow sinh cosh tanh asinh acosh atanh rad deg getenv putenv tparam tgoto crtbynam crtbypth getwind setwind modlink modload munlink _os9 getime setime stacksiz freemem skipbl skipwd'.split()
    aliases=names();symbols=sorted({aliases.get(name,name[:8]) for name in api})
    source=' section code\n export main\nmain:\n clra\n clrb\n rts\n'
    for symbol in symbols:source+=' extern '+symbol+'\n fdb '+symbol+'\n'
    target=work/'exports.s';target.write_text(source)
    run(['lwasm','--format=obj','-o',work/'exports.o',target])
    run(['lwlink','--format=os9','-s',home/'os9c3.ld','-o',work/'exports',home/'crt0.o',work/'exports.o',home/'fpinit.o','-L'+str(home),'-lcgfx','-ltermcap','-lc3','-lc3lw'])
    print('Native feature exports: %d linked' % len(symbols))


if __name__=='__main__':main()
