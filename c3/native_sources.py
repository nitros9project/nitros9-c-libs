"""Build-time syntax and symbol selection for the native C3 compiler."""
import hashlib
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKENS = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_]\w*(?:\$\w+)?', re.S)


def interfaces():
    result = {}
    for path in sorted((ROOT / 'include').rglob('*.h')):
        text = re.sub(r'/\*.*?\*/', '', path.read_text(), flags=re.S)
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
    aliases['registers_6809'] = 'os9_regs'
    return aliases


def c_view(text, *, header=False, aliases=None):
    aliases = aliases or names()
    comments = re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|/\*.*?\*/|//[^\n]*', re.S)
    text = comments.sub(lambda m: '\n'*m[0].count('\n') if m[0].startswith('/*') else '' if m[0].startswith('//') else m[0], text)
    def token(match):
        word = match[0]
        if word.startswith(('"', "'")):
            return word
        if word in ('const', 'volatile'):
            return ''
        return aliases.get(word, word.replace('$', '_'))
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
    for path in (ROOT / 'include').rglob('*.h'):
        target = destination / path.relative_to(ROOT / 'include')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text('#include <c3names.h>\n'+c_view(path.read_text(), header=True, aliases=aliases))
    (destination / 'c3names.h').write_text('#ifndef NITROS9_C3_NAMES_H\n#define NITROS9_C3_NAMES_H\n'+'\n'.join('#define ' + k + ' ' + v for k, v in aliases.items() if k != v) + '\n#endif\n')
    return aliases
