"""Keep independently reachable assembly bodies in separate archive members."""
import re
from native_asm import parse, cfg, DIRECTIVES, CALLS


def split(text):
    lines=[parse(s) for s in text.splitlines()]
    exports=set()
    for x in lines:
        if x.op=='export':exports.add(x.label or x.operand)
    labels={x.label:i for i,x in enumerate(lines) if x.label and x.op not in DIRECTIVES}
    # Calls into another body become ordinary archive references. Export those
    # existing private entries, so using getstat need not pull setstat or the
    # modern API entry points from the same source unit. No code is generated.
    private={x.operand for x in lines if x.op in CALLS and x.operand in labels}
    entries={name:labels[name] for name in exports|private if name in labels}
    if len(entries)<2:return [text]
    groups=[]
    for name,start in sorted(entries.items()):
        body=cfg(start,lines,labels,{})
        overlap=[g for g in groups if g[1]&body]
        symbols={name}
        for g in overlap:
            symbols.update(g[0]);body.update(g[1]);groups.remove(g)
        groups.append((symbols,body))
    result=[]
    for symbols,body in groups:
        kept=[symbol+' EXPORT' for symbol in sorted(symbols-exports)]
        dependencies={lines[i].operand for i in body if lines[i].op in CALLS and lines[i].operand in entries and lines[i].operand not in symbols}
        kept.extend(symbol+' EXTERNAL' for symbol in sorted(dependencies))
        for i,x in enumerate(lines):
            if x.op=='export' and (x.label or x.operand) not in symbols:continue
            if x.op in DIRECTIVES:
                kept.append(x.raw)
            elif i in body:
                kept.append(x.raw)
            elif not x.op and not x.label:
                kept.append(x.raw)
        result.append('\n'.join(kept)+'\n')
    return result
