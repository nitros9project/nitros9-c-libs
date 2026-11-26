"""Select C3 register arguments in shared assembly at build time.

This lowers the function bodies themselves. It emits neither ABI trampolines
nor calls to a second, foreign-ABI copy of a function.
"""
from dataclasses import dataclass
import re

BRANCHES = {'bra', 'lbra', 'jmp'}
CALLS = {'bsr', 'lbsr', 'jsr'}
CONDITIONAL = {'beq','bne','bmi','bpl','bcs','bcc','bhi','bls','bgt','bge','blt','ble','bvc','bvs','lblo','lbhs','blo','bhs'}
DIRECTIVES = {'equ','set','export','extern','external','import','section','endsect','endsection','use','rmb','rzb','fcb','fdb','fcc','fqb'}


@dataclass
class Line:
    raw: str
    label: str = ''
    op: str = ''
    operand: str = ''
    note: str = ''


def parse(raw):
    line = raw.split(';', 1)
    code = line[0].rstrip()
    note = line[1] if len(line)>1 else ''
    if not code.strip() or code.lstrip().startswith('*'):
        return Line(raw)
    label = ''
    if not code[0].isspace():
        parts = code.split(None, 1)
        label = parts[0].rstrip(':')
        code = parts[1] if len(parts)>1 else ''
    parts = code.split(None, 1)
    return Line(raw, label, parts[0].lower() if parts else '', parts[1].strip() if len(parts)>1 else '', note)


def emit(line, *, op=None, operand=None):
    op = line.op if op is None else op
    operand = line.operand if operand is None else operand
    return (line.label + ':' if line.label else '') + ('\t' + op + '\t' + operand if op else '') + (' ;' + line.note if line.note else '')


def arglist(args):
    if not args or args == 'void': return []
    level = 0
    start = 0
    result = []
    for i, c in enumerate(args):
        if c in '([': level += 1
        elif c in ')]': level -= 1
        elif c == ',' and not level:
            result.append(args[start:i].strip()); start=i+1
    result.append(args[start:].strip())
    return result


def integer(value):
    try: return int(value.strip(), 0)
    except ValueError: return None


def cfg(start, lines, labels, entries):
    todo = [start]
    visited = set()
    while todo:
        i = todo.pop()
        if i in visited or i >= len(lines): continue
        if i != start and i in entries: continue
        visited.add(i)
        x = lines[i]
        target = labels.get(x.operand)
        if x.op in ('rts', 'rti') or (x.op == 'puls' and 'pc' in x.operand.lower().split(',')):
            continue
        if x.op in BRANCHES:
            if target is not None: todo.append(target)
            continue
        if x.op.removeprefix('l') in CONDITIONAL or x.op in CONDITIONAL:
            if target is not None: todo.append(target)
        # Calls are separate frames. Their bodies do not inherit this entry's
        # argument spill, but execution resumes at the following instruction.
        todo.append(i+1)
    return visited


def lower(text, specs, *, name='unit'):
    lines = [parse(s) for s in text.splitlines()]
    labels = {x.label:i for i,x in enumerate(lines) if x.label and x.op not in DIRECTIVES}
    entries = {}
    for symbol, spec in specs.items():
        if symbol in labels:
            entries[labels[symbol]] = (symbol, spec)
    # Multiple C API aliases can name one entry body (index/strchr). Select
    # its frame once, otherwise an alias can add a second argument spill.
    bodies={}
    for index, value in entries.items():
        first=index+1
        while first<len(lines) and (not lines[first].op or lines[first].op in DIRECTIVES):first+=1
        bodies[first]=(index,value)
    entries={index:value for index,value in bodies.values()}
    changes = {}
    before = {}
    modes = {}
    returns = {}
    long_exits = set()
    conditional_returns = {}
    parameters = {}
    report = []
    for index, (symbol, spec) in entries.items():
        args = arglist(spec['args'])
        if not args or (('*' not in args[0] and '[' not in args[0]) and re.search(r'\b(long|float|double|time_t|off_t)\b', args[0])):
            modes[index] = 'stack'; continue
        decls=[]
        first_op=None
        for j in range(index+1, len(lines)):
            x=lines[j]
            if x.op == 'equ':
                value=integer(x.operand)
                if value is not None: decls.append((j,x,value))
            elif x.op and x.op not in DIRECTIVES:
                first_op=j;break
        ret = next(((j,x,v) for j,x,v in decls if x.label.endswith('_ret')), None)
        if ret is None or first_op is None:
            raise ValueError(name+': missing parameter layout for '+symbol)
        retvalue=ret[2]
        firstbase=retvalue+2
        # The shared long-return assembly has an explicit hidden destination;
        # native long-return selection is handled before this lowering pass.
        incoming=[]
        seenret=False
        for j,x,value in decls:
            if j == ret[0]: seenret=True;continue
            if not seenret:continue
            if re.search(r'local|scratch|temporary|staged|frame size',x.note,re.I):continue
            if value >= firstbase and x.label.startswith('stk_'):
                incoming.append((j,x,value))
        first=[(j,x,v) for j,x,v in incoming if firstbase <= v < firstbase+2]
        if not first:
            raise ValueError(name+': no first argument fields for '+symbol)
        fields={x.label for _,x,_ in first}
        refs=[(j,x) for j,x in enumerate(lines) if x.op not in DIRECTIVES and any(re.search(r'\b'+re.escape(f)+r'\b',x.operand) for f in fields)]
        mode='spill'
        load=None
        hoist=False
        if len(refs)==1 and (name not in {'fopen','getc','strings','stringsu','create','sets'} or symbol=='_strend') and name!='dir':
            j,x=refs[0]
            if first_op <= j and (next((k for k in sorted(entries) if k>index),len(lines))>j) and x.op in ('ldd','ldx','ldy','ldu','lda','ldb'):
                prefix=[t for t in lines[first_op:j] if t.op]
                if all(t.op in ('pshs','ldx','ldy','ldu','leas','leax','leay','leau') for t in prefix):
                    mode='register';load=(j,x)
                elif x.op in ('ldx','ldy','ldu') and all(t.op not in BRANCHES|CALLS|CONDITIONAL and not re.search(r'\b'+x.op[-1]+r'\b',t.operand,re.I) and t.op[-1:]!=x.op[-1] for t in prefix):
                    mode='register';load=(j,x);hoist=True
        modes[index]=mode
        reachable=cfg(index,lines,labels,entries)
        if mode=='register':
            j,x=load
            if x.op=='ldd': replacement=''
            elif x.op in ('ldx','ldy','ldu'): replacement='\ttfr\td,'+x.op[-1]
            elif x.op=='lda': replacement='\ttfr\tb,a'
            else: replacement=''
            k=j+1
            while k<len(lines) and not lines[k].op:k+=1
            need_flags=k<len(lines) and lines[k].op in ('beq','bne','bmi','bpl','lbeq','lbne','lbmi','lbpl')
            if hoist:
                before[first_op]=replacement
                replacement='\tcmp'+x.op[-1]+'\t#0' if need_flags else ''
            elif need_flags:
                replacement += '\n\t'+('tst'+x.op[-1] if x.op in ('lda','ldb') else 'cmpd')+('\t#0' if x.op not in ('lda','ldb') else '')
            changes[j]=emit(Line('',x.label))+'\n'+replacement
            for d,field,value in incoming:
                parameters[field.label]=(value-2,d,field)
        else:
            mask = [r.strip().lower() for r in lines[first_op].operand.split(',')]
            has_conditional_exit=any(lines[k].op.removeprefix('l') in CONDITIONAL and lines[k].operand not in labels for k in reachable)
            combined = name!='gs' and not has_conditional_exit and lines[first_op].op == 'pshs' and set(mask) <= {'u','y'}
            saved = 2*len(mask) if combined else 0
            mode = 'combined' if combined else 'spill'
            modes[index] = mode
            if combined:
                changes[first_op] = emit(lines[first_op], operand='d,'+','.join(mask))
                for d,field,value in decls:
                    if d < ret[0]: parameters[field.label]=(value+2,d,field)
            else:
                before[first_op]='\tpshs\td ; native first argument local'
            for d,field,value in first: parameters[field.label]=(value-saved-2,d,field)
            parameters[ret[1].label]=(retvalue+2,ret[0],ret[1])
            for j in reachable:
                x=lines[j]
                if x.op=='rts' or (x.op=='puls' and 'pc' in x.operand.lower().split(',')):
                    returns.setdefault(j,set()).add(mode)
                elif x.op in BRANCHES and x.operand not in labels:
                    returns.setdefault(j,set()).add(mode+'-tail')
        for j in reachable:
            x=lines[j]
            if x.op=='rts' or (x.op=='puls' and 'pc' in x.operand.lower().split(',')):
                returns.setdefault(j,set()).add(mode)
        for j in reachable:
            if lines[j].op.removeprefix('l') in CONDITIONAL and lines[j].operand not in labels:conditional_returns.setdefault(j,set()).add(mode)
            if lines[j].op in BRANCHES and lines[j].operand not in labels:returns.setdefault(j,set()).add(mode+'-tail')
        if '*' not in spec['return'] and re.search(r'\b(long|time_t|off_t)\b',spec['return']):long_exits.update(reachable)
        report.append({'symbol':symbol,'mode':mode,'first_fields':sorted(fields)})
    for key,(value,j,field) in parameters.items():
        changes[j]=emit(field,operand=str(value))
    for j, flags in returns.items():
        normal = {flag.removesuffix('-tail') for flag in flags}
        if len(normal)>1:
            raise ValueError(name+': shared exit needs explicit native frame selection at '+str(j+1)+': '+str(flags))
        x=lines[j]
        mode=next(iter(normal), next(iter(flags)).removesuffix('-tail'))
        if mode not in ('spill','combined'): continue
        label=(x.label+':' if x.label else '')
        discard='d' if j in long_exits else 'x'
        if x.op in BRANCHES:
            k=j-1
            while k>=0 and not lines[k].op:k-=1
            if mode=='combined' and lines[k].op=='puls' and set(lines[k].operand.split(',')) <= {'y','u'}:
                changes[k]=emit(lines[k],operand=discard+','+lines[k].operand)
            else:
                changes[j]=label+'\n\tleas\t2,s\n\t'+x.op+'\t'+x.operand
        elif mode=='combined':
            # Pointer-returning leaves often reload the saved first argument
            # just to discard that same word into X. Return it with PULS D.
            k=j-1
            while k>=0 and (not lines[k].op or lines[k].op in DIRECTIVES):k-=1
            load=lines[k]
            match=re.fullmatch(r'([A-Za-z_]\w*)([+-]\d+)?,s',load.operand)
            if discard=='x' and load.op=='ldd' and match and match[1] in parameters:
                offset=parameters[match[1]][0]+int(match[2] or 0)
                if offset==0:
                    changes[k]=emit(load,op='',operand='')
                    discard='d'
            mask=[r.strip().lower() for r in x.operand.split(',')] if x.op=='puls' else ['pc']
            if discard in mask:
                raise ValueError(name+': combined exit already pops X at '+str(j+1))
            changes[j]=emit(x,op='puls',operand=','.join([discard]+mask))
        else:
            mask=[r.strip() for r in x.operand.split(',') if r.strip().lower()!='pc'] if x.op=='puls' else []
            changes[j]=label+ ('\n\tpuls\t'+','.join(mask) if mask else '')+'\n\tpuls\t'+discard+',pc'
    inverse={'beq':'bne','bne':'beq','bcs':'bcc','bcc':'bcs','blo':'bhs','bhs':'blo','bhi':'bls','bls':'bhi','bgt':'ble','ble':'bgt','bge':'blt','blt':'bge','bmi':'bpl','bpl':'bmi','bvc':'bvs','bvs':'bvc'}
    for j, flags in conditional_returns.items():
        if flags=={'register'} or flags=={'stack'}:continue
        if flags!={'spill'}:raise ValueError(name+': conditional exit frame conflict '+str(flags))
        x=lines[j];label='.c3_continue_'+str(j)
        changes[j]=(x.label+':' if x.label else '')+'\n\t'+inverse[x.op.removeprefix('l')]+'\t'+label+'\n\tleas\t2,s\n\tlbra\t'+x.operand+'\n'+label+':'
    rendered=[]
    for i,line in enumerate(lines):
        if i in before:rendered.append(before[i])
        rendered.append(changes.get(i,line.raw))
    return '\n'.join(rendered)+'\n',report
