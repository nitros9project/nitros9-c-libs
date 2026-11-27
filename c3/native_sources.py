"""Build-time syntax and symbol selection for the native C3 compiler."""
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*(?:\$\w+)?', re.S)


def split_declarations(text):
    pattern = re.compile(r'(?m)^([ \t]*(?:extern[ \t]+)?(?:void|int|unsigned|long|float|double|char)[ \t*]+)([A-Za-z_]\w*\([^;{}]*\)[ \t]*);')
    def split(match):
        declarations = re.split(r'(?<=\)),[ \t]*(?=[A-Za-z_]\w*\()', match[2])
        return '\n'.join(match[1]+part+';' for part in declarations)
    return pattern.sub(split,text)


def interfaces():
    result = {}
    for path in sorted([*(ROOT / 'include').rglob('*.h'), *(ROOT / 'cgfx/include').rglob('*.h')]):
        text = split_declarations(re.sub(r'/\*.*?\*/', '', path.read_text(), flags=re.S))
        for ret, name, args in re.findall(r'(?m)^([A-Za-z_][^\n;{}]*?)\b([A-Za-z_]\w*)\s*\(([^;{}]*?)\);', text, re.S):
            if not ret.strip().startswith('typedef'):
                result[name] = {'return': ret.strip(), 'args': args.strip()}
    return result


def names():
    api = interfaces()
    api.update({n: {} for n in ['pflinit', '_flush', 'setbase', 'ibrk', 'getsp']})
    aliases = {}
    used = set()
    for name in sorted(api, key=lambda n: (len(n), n)):
        candidate = name[:8]
        if candidate in used or candidate in {'register', 'unsigned', 'continue', 'volatile'}:
            candidate = 'n9' + hashlib.sha256(name.encode()).hexdigest()[:6]
        aliases[name] = candidate
        used.add(candidate)
    # Modern and historical C3 graphics names select the same native body.
    graphics = json.loads((ROOT/'c3/cgfx_names.json').read_text())
    for modern, legacy in graphics.items():
        aliases[modern] = aliases.get(legacy, legacy[:8])
    aliases['_getsp']='getsp'
    aliases['registers_6809'] = 'os9_regs'
    return aliases


def c_view(text, *, header=False, aliases=None):
    aliases = aliases or names()
    text = text.replace('\f','\n')
    comments = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*', re.S)
    text = comments.sub(lambda m: '\n'*m[0].count('\n') if m[0].startswith('/*') else '' if m[0].startswith('//') else m[0], text)
    def token(match):
        word = match[0]
        if word.startswith(('"', "'")):
            return word
        if word in ('const', 'volatile'):
            return ''
        return aliases.get(word, word.replace('$', '_'))
    # C3 predates adjacent string-literal concatenation. Resolve it before
    # compilation, bounding hexadecimal escapes before removing the boundary.
    literal = r'"(?:\\.|[^"\\])*"'
    adjacent = re.compile('('+literal+r')(?:[ \t\r\n]+)('+literal+')')
    def join_literals(match):
        left=re.sub(r'\\x([0-9a-fA-F]+)',lambda m:'\\%03o' % int(m[1],16),match[1][:-1])
        return left+match[2][1:]
    while adjacent.search(text):text=adjacent.sub(join_literals,text)
    text = TOKENS.sub(token, text)
    text = re.sub(r'\bunsigned\s+char\b', 'char', text)
    text = re.sub(r'\bunsigned\s+long\b', 'long', text)
    text = re.sub(r'\bunsigned\s+short\b', 'unsigned', text)
    text = re.sub(r'(?i)([0-9a-fx]+)UL\b', r'\1L', text)
    text = re.sub(r'(?i)\b(0x[0-9a-f]+|[0-9]+)U\b', r'((unsigned)\1)', text)
    text = re.sub(r'([0-9]\.[0-9]+)f\b', r'\1', text)
    text = re.sub(r'\basm\s*\{([^{}]*)\}', lambda m: '\n#asm\n'+m[1]+'\n#endasm\n', text)
    text = re.sub(r'(\b(?:int|void|char|unsigned|long)\s*\(\s*\*\s*\w+\s*\))\([^()]*\)', r'\1()', text)
    if header:
        text = split_declarations(text)
        # Dollar aliases can become self-definitions after symbol selection.
        text = re.sub(r'(?m)^#[ \t]*define[ \t]+(\w+)[ \t]+\1[ \t]*$', '', text)
        # Legacy stdio exports nonstandard boolean macros. Existing C3 code
        # defines its own; redefinitions leak diagnostics into optimizer input.
        text = re.sub(r'(?m)^#[ \t]*define[ \t]+(?:TRUE|FALSE)[^\n]*', '', text)
        # C3 misparses a function returning a function-pointer typedef as
        # a pointer variable. OS-9 handler addresses and int are one word;
        # expose the same D result as an opaque integer in this header view.
        text = re.sub(r'\bsighandler_t\s+signal\s*\([^;]*\);', 'int signal();', text)
        text = re.sub(r'\(\(sighandler_t\)\s*([01])\)', r'\1', text)
        text = text.replace('struct os_time;', '').replace('typedef struct os_time _os_time;', '#define _os_time struct os_time')
        # Named ANSI prototype parameters pollute C3's old symbol table. The
        # generated declarations retain result types and use its K&R form.
        text = re.sub(r'(?m)^(?!typedef)([ \t]*(?:extern[ \t]+)?[\w \t*]+?[ \t*])(\w+)\([^;{}]*\)[ \t]*;', r'\1\2();', text)
    return text


def write_headers(destination):
    aliases = names()
    for folder in (ROOT/'include', ROOT/'cgfx/include'):
      for path in folder.rglob('*.h'):
        target = destination / path.relative_to(folder)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('#include <c3names.h>\n'+c_view(path.read_text(), header=True, aliases=aliases))
    # Historical assembler clients include stdio.a. Derive its offsets and
    # byte flags from the canonical assembler layout, rather than retaining
    # another FILE definition in the compiler repository.
    layout=(ROOT/'include/stdio.d').read_text()
    values={name:int(value.replace('$','0x'),0) for name,value in re.findall(r'(?m)^(\w+)[ \t]+equ[ \t]+(\$[0-9a-fA-F]+|[0-9]+)\b',layout)}
    fields={'_ptr':'FILE_PTR','_base':'FILE_BASE','_end':'FILE_END',
            '_flag':'FILE_FLAG','_fd':'FILE_FD','_save':'FILE_SAVE',
            '_bufsiz':'FILE_BUFSIZ','_iobsiz':'FILE_SIZE',
            '_WRITTEN':'_WRITTEN_HIGH','_INIT':'_INIT_HIGH'}
    fields.update({name:name for name in ('_READ','_WRITE','_UNBUF','_BIGBUF','_EOF','_ERR','_SCF','_RBF')})
    legacy={name:values[canonical] for name,canonical in fields.items()}
    legacy['_DEVMASK']=values['_SCF']|values['_RBF']
    legacy['_NFILE']=values['FILE_STDIO_COUNT']+values['FILE_USER_COUNT']
    legacy['BUFSIZ']=int(re.search(r'^#define[ \t]+BUFSIZ[ \t]+([0-9]+)',(ROOT/'include/stdio.h').read_text(),re.M)[1])
    (destination/'stdio.a').write_text('* Generated from canonical stdio.d and stdio.h\n'+'\n'.join(name+' equ '+str(value) for name,value in legacy.items())+'\n')
    (destination / 'c3names.h').write_text('#ifndef NITROS9_C3_NAMES_H\n#define NITROS9_C3_NAMES_H\n#ifndef NITROS9_C3\n#define NITROS9_C3 1\n#endif\n'+'\n'.join('#define ' + k + ' ' + v for k, v in aliases.items() if k != v) + '\n#endif\n')
    return aliases
