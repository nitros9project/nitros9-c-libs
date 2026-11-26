"""Select the native C3 accumulator return in shared long-result assembly."""
import re
from native_asm import parse, emit, integer


def select(text, name):
    lines=[parse(s) for s in text.splitlines()]
    hidden={x.label:integer(x.operand) for x in lines if x.op=='equ' and 'hidden' in x.note.lower() and integer(x.operand) is not None and x.label.startswith('stk_')}
    if not hidden:return text
    changes={}; active=None
    for i,x in enumerate(lines):
        if x.op=='equ' and x.label.endswith('_ret'):
            active=None
        if x.label in hidden:
            active=hidden[x.label]
            continue
        if x.op and x.op!='equ':active=None
        if active is not None and x.op=='equ' and x.label.startswith('stk_'):
            value=integer(x.operand)
            if re.search(r'local|scratch|saved|return address',x.note,re.I) and not re.search(r'argument|offset|origin|stream',x.note,re.I):active=None
            if active is not None and value is not None and value>active:
                changes[i]=emit(x,operand=str(value-2))
        if x.op in ('ldx','ldu') and any(re.search(r'\b'+key+r'\b',x.operand) for key in hidden):
            changes[i]=emit(x,op='lea'+x.op[-1],operand='_flacc,y')
    if name=='fseek':
        for i,x in enumerate(lines):
            if x.op=='equ' and x.label.startswith('stk_fseek_') and x.label.endswith(('_stream','_pos','_whence')):
                line=parse(changes.get(i,x.raw))
                changes[i]=emit(line,operand=str(integer(line.operand)-2))
            if x.op=='ldu' and 'stk_fseek_entry_stream' in x.operand:
                changes[i]='\ttfr\td,u\n\tcmpu\t#0'
    # atol uses a local accumulator; its return pointer must survive teardown.
    if name=='atol':
        for i,x in enumerate(lines):
            if x.op=='puls' and 'pc' in x.operand:
                changes[i]='\tleax\t_flacc,y\n'+changes.get(i,x.raw)
    return '_flacc EXTERNAL\n'+'\n'.join(changes.get(i,x.raw) for i,x in enumerate(lines))+'\n'
