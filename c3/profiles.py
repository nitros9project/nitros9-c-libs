"""Explicit selection for assembly bodies with cached arguments or callbacks."""
import re
from native_asm import parse, emit


def select(text,name):
    lines=[parse(s) for s in text.splitlines()]
    changes={}
    if name in ('fputs','puts','putw'):
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand.lower() in ('d,x','d,u'):
                changes[i]=emit(x,operand=x.operand.split(',')[1])
            if name=='fputs' and x.op=='stb' and x.operand=='1,s':changes[i]=emit(x,op='clra',operand='')
            if name=='puts' and x.op=='std' and x.operand==',s':changes[i]=''
            if name=='putw':
                if x.op=='stb' and x.operand=='1,s':changes[i]=emit(x,op='clra',operand='')
                if x.op=='ldb' and 'stk_putw_word+7' in x.operand:changes[i]=emit(x,operand=x.operand.replace('+7','+5'))+'\n\tclra'
                if x.op=='ldb' and 'stk_putw_word+2' in x.operand:changes[i]=x.raw+'\n\tclra'
            if x.op=='leas' and x.operand=='4,s':changes[i]=emit(x,operand='2,s')
    if name=='printf':
        # Native argument lowering and the compact float path put these
        # three formatter targets within signed 8-bit branch range.
        for i,x in enumerate(lines):
            if (x.op,x.operand.split()[0] if x.operand else '') in {('lbeq','case_d'),('lbeq','case_u'),('lbra','L0047')}:
                changes[i]=emit(x,op=x.op[1:])
    if name=='fopen':
        for i,x in enumerate(lines):
            if x.op=='ldd' and x.operand=='stk_fdopen_fd,s':
                # D is still the native first argument after LDU/LDX setup.
                changes[i]=emit(x,op='',operand='')
    if name=='debug':
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand=='u' and i>0 and lines[i-1].op=='leau' and 'format' in lines[i-1].operand:
                changes[i]=emit(x,op='tfr',operand='u,d')
            if x.op=='leas' and x.operand=='2,s' and 'format' in x.note:changes[i]=''
    if name=='putc':
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand=='d,x':changes[i]=emit(x,operand='x')
            if x.op in ('bsr','lbsr') and x.operand in ('__os_write','__os_writeln','_write','_writeln'):
                changes[i]=(x.label+':' if x.label else '')+'\n\tldd\t8,u\n\t'+x.op+'\t'+x.operand
            if x.op=='leas' and x.operand=='6,s':changes[i]=emit(x,operand='4,s')
    if name=='getc':
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand=='d,x':changes[i]=emit(x,operand='x')
            if x.op in ('lbsr','bsr') and x.operand in ('_read','_readln'):
                changes[i]=(x.label+':' if x.label else '')+'\n\tldd\tFILE_FD,u\n\t'+x.op+'\t'+x.operand
            if x.op=='leas' and x.operand=='6,s':changes[i]=emit(x,operand='4,s')
    if name=='setbase':
        for i,x in enumerate(lines):
            if x.label in ('stk_setbase_gs_optbuf','stk_setbase_gs_frame_size') and x.op=='equ':changes[i]=emit(x,operand='('+x.operand+')-2')
            if x.op=='pshs' and x.operand=='d' and i+1<len(lines) and lines[i+1].operand=='_getstat':changes[i]=''
    if name=='qsort':
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand=='u' and i+1<len(lines) and lines[i+1].operand=='[_QCMP,y]':changes[i]=emit(x,op='tfr',operand='u,d')
            if x.op=='leas' and x.operand=='4,s':changes[i]=emit(x,operand='2,s')
    if name in ('signal','intercept'):
        for i,x in enumerate(lines):
            if x.op=='pshs' and x.operand=='d' and i+1<len(lines) and lines[i+1].op=='jsr':changes[i]=''
            if name=='intercept' and x.op=='leas' and x.operand=='2,s':changes[i]=''
            if name=='signal' and x.op=='puls' and x.operand=='d,x':changes[i]=emit(x,operand='x')
    if name=='htol':
        for i,x in enumerate(lines):
            if x.op=='leau' and x.operand=='_flacc,y':
                # X already names the native accumulator; Y currently names
                # the ctype table, so no hidden-destination copy is needed.
                for j in range(i,i+5):changes[j]=''
    if name=='stat':
        for i,x in enumerate(lines):
            if x.op=='equ' and x.label.startswith('stk_') and x.label.endswith(('_code','_path','_p1','_p2','_p3','_p4')):
                changes[i]=emit(x,operand=str(int(x.operand)-2))
            if x.op=='ldb' and ('stk_do_getstat_code' in x.operand or 'stk_do_setstat_code' in x.operand):
                changes[i]=emit(x,op='tstb',operand='')
    if name=='sets':
        for i,x in enumerate(lines):
            if x.label=='stk_bitaddr_set' and x.op=='equ':changes[i]=emit(x,operand='2')
    # CMOC copies a hidden destination from _flacc. Native long results
    # already use _flacc, so those stores would copy the accumulator to itself.
    for i,x in enumerate(lines):
        if x.op=='leax' and x.operand=='_flacc,y':
            sequence=[(t.op,t.operand) for t in lines[i+1:i+5]]
            if sequence==[('ldd','_flacc,y'),('std','0,x'),('ldd','_flacc+2,y'),('std','2,x')]:
                for j in range(i+1,i+5):changes[j]=emit(lines[j],op='',operand='')
                if i>0 and lines[i-1].op in ('bsr','lbsr') and lines[i-1].operand=='_ladd':changes[i]=emit(x,op='',operand='')
    return '\n'.join(changes.get(i,x.raw) for i,x in enumerate(lines))+'\n'
