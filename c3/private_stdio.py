"""Use the existing U-held FILE pointer for private stdio helper calls."""
from native_asm import parse, emit, cfg, DIRECTIVES


def select(text, name):
    lines=[parse(s) for s in text.splitlines()]
    labels={x.label:i for i,x in enumerate(lines) if x.label and x.op not in DIRECTIVES}
    changes={}
    def executable(index, step):
        index+=step
        while 0<=index<len(lines) and (not lines[index].op or lines[index].op in DIRECTIVES):index+=step
        return index
    for helper in ('_setbase','_flush'):
        if helper not in labels:continue
        entry=labels[helper]
        prologue=executable(entry,1)
        load=executable(prologue,1)
        if lines[prologue].op!='pshs' or lines[prologue].operand!='u' or (lines[load].op,lines[load].operand)!=('ldu','stk_'+helper[1:]+'_file+2,s'):
            raise ValueError(name+': unexpected private FILE helper frame: '+helper)
        changes[prologue]=emit(lines[prologue],op='',operand='')
        changes[load]=emit(lines[load],op='',operand='')
        for i in cfg(entry,lines,labels,{}):
            x=lines[i]
            if x.op=='puls' and x.operand=='u,pc':changes[i]=emit(x,op='rts',operand='')
    for i,x in enumerate(lines):
        if x.op not in ('bsr','lbsr','jsr') or x.operand not in ('_setbase','_flush'):continue
        push=executable(i,-1);cleanup=executable(i,1)
        if lines[push].op!='pshs' or lines[push].operand!='u':raise ValueError(name+': private FILE call does not stage U')
        if not ((lines[cleanup].op=='leas' and lines[cleanup].operand=='2,s') or (lines[cleanup].op=='std' and lines[cleanup].operand==',s++')):
            raise ValueError(name+': unexpected private FILE call cleanup')
        # Both helpers preserve U. _flush returns flags matching its 0/-1 D
        # result, so callers do not need the former STD ,S++ flag refresh.
        for j in (push,cleanup):changes[j]=emit(lines[j],op='',operand='')
    return '\n'.join(changes.get(i,x.raw) for i,x in enumerate(lines))+'\n'
