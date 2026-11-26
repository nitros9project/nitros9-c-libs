"""Select register argument placement at assembly call sites."""
import re
from native_asm import parse, emit, arglist


def lower(text, specs, name):
    if name in ('cfinish','fputs','puts','putw','debug'):return text,[]  # native conditional entry calls directly
    lines=[parse(s) for s in text.splitlines()]
    changes={};report=[]
    labels={x.label:i for i,x in enumerate(lines) if x.label}
    def previous(i):
        i-=1
        while i>=0 and not lines[i].op:i-=1
        return i
    def following(i):
        i+=1
        while i<len(lines) and not lines[i].op:i+=1
        return i
    for i,x in enumerate(lines):
        if x.op not in ('bsr','lbsr','jsr') or x.operand not in specs:continue
        if name=='fseek' and x.operand=='_fseek':continue  # explicit native rewind body
        if name=='setbase' and x.operand=='_getstat':continue
        if name=='putc' and x.operand in ('__os_write','__os_writeln','_write','_writeln'):continue
        if name=='getc' and x.operand in ('_read','_readln'):continue
        spec=specs[x.operand];args=arglist(spec['args'])
        if not args:continue
        if '*' not in args[0] and '[' not in args[0] and re.search(r'\b(long|float|double|time_t|off_t)\b',args[0]):continue
        long_result=bool(re.search(r'\b(long|time_t|off_t)\b',spec['return'])) and '*' not in spec['return']
        removed=0;j=previous(i)
        if long_result and lines[j].op=='pshs' and lines[j].operand=='x,u':
            after=following(i);cleanup=lines[after]
            if cleanup.op!='leas':raise ValueError(name+': hidden combined cleanup changed')
            changes[j]=emit(lines[j],op='tfr',operand='u,d')
            k=previous(j)
            if lines[k].op=='leax' and '_flacc' in lines[k].operand:changes[k]=''
            changes[after]=emit(cleanup,operand='('+cleanup.operand.rsplit(',',1)[0]+')-4,s')
            k=following(after)
            if k<len(lines) and lines[k].op=='leax' and lines[k].operand=='_flacc,y':changes[k]=emit(lines[k],op='',operand='')
            report.append({'callee':x.operand,'line':i+1,'removed_argument_bytes':4})
            continue
        if long_result:
            if lines[j].op!='pshs' or lines[j].operand.lower()!='x':
                raise ValueError(name+': hidden long call needs profile at '+str(i+1)+': '+x.operand)
            changes[j]='';removed+=2
            k=previous(j)
            if lines[k].op=='leax' and '_flacc' in lines[k].operand:
                changes[k]='';j=previous(k)
            else:j=k
        push=lines[j]
        after=following(i)
        if after<len(lines) and lines[after].op in ('bra','lbra') and lines[after].operand in labels:after=labels[lines[after].operand]
        while after<len(lines) and not lines[after].op:after+=1
        cleanup=lines[after] if after<len(lines) else None
        straightforward=cleanup and cleanup.op=='leas' and cleanup.operand.lower().endswith(',s')
        if push.op=='pshs' and straightforward:
            regs=[r.strip().lower() for r in push.operand.split(',')]
            first=next((r for r in ('d','x','y','u') if r in regs),None)
            if first is None:raise ValueError(name+': non-word first call argument '+str(i+1))
            regs.remove(first)
            code=(push.label+':' if push.label else '')
            if regs:code+='\n\tpshs\t'+','.join(regs)
            if first!='d':code+='\n\ttfr\t'+first+',d'
            changes[j]=code;removed+=2
            amount=cleanup.operand.rsplit(',',1)[0]
            changes[after]=emit(cleanup,operand='('+amount+')-'+str(removed)+',s')
        elif name=='sets' and x.operand=='_copyset' and push.op=='pshs' and push.operand=='d,x':
            changes[j]=emit(push,operand='x')
            if cleanup.op!='puls' or cleanup.operand!='d,x': raise ValueError('copyset teardown changed')
            changes[after]=emit(cleanup,operand='x')
        elif len(args)==1 and not long_result:
            # A cached unary argument remains an ordinary caller local.
            changes[i]=(x.label+':' if x.label else '')+'\n\tldd\t,s\n\t'+x.op+'\t'+x.operand
        else:
            raise ValueError(name+': cached/multi-argument call needs native profile at '+str(i+1)+': '+x.operand)
        if long_result:
            k=following(after)
            if k<len(lines) and lines[k].op=='leax' and lines[k].operand=='_flacc,y':changes[k]=emit(lines[k],op='',operand='')
        report.append({'callee':x.operand,'line':i+1,'removed_argument_bytes':removed})
    return '\n'.join(changes.get(i,x.raw) for i,x in enumerate(lines))+'\n',report
