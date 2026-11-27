"""Prepare preserved RMA assembly bodies for the shared native C3 build."""
from pathlib import Path
import re
import ast
import operator
import subprocess


def expand(path, seen=()):
    path = Path(path)
    if path in seen:
        raise ValueError('Recursive assembler include: '+str(path))
    lines = []
    for line in path.read_text(encoding='latin1').splitlines():
        include = re.match(r'\s+use\s+(\S+)', line, re.I)
        if include:
            lines.append(expand(path.parent/include[1], (*seen,path)))
        elif re.match(r'\s+(?:ifp1|endc|opt|pag|page|spc)\b',line,re.I):
            continue
        else:
            lines.append(line)
    return '\n'.join(lines)+'\n'


def prepare(text, c3):
    text=re.sub(r'(?mi)^[ \t]*(?:ifp1|endc|opt|pag|page|spc)\b[^\n]*','',text)
    # LWASM does not retain a trailing dollar sign on a defined symbol.
    text=text.replace('DECTAB$','DECTAB_d')
    isdefs=bool(re.search(r'(?i)\bpsect[ \t]+OS9Defs,',text))
    if isdefs:
        text=re.sub(r'\b([A-Za-z_][\w.]*)\$([A-Za-z_]\w*)',r'\1_\2',text)
        text=re.sub(r'\bSS\.', 'SS_',text)
    text=re.sub(r'(?m)^([ \t]+|[A-Za-z_][\w.$]*:?[ \t]+)([A-Za-z]+)(?=[ \t]|$)',lambda m:m[1]+m[2].lower(),text)
    text=re.sub(r'(?m)^([ \t]*)(?:esect|ends)\b',r'\1endsect',text)
    # Use the shared ABI constants, accepting historical case and dot spelling.
    abi = (Path(__file__).resolve().parents[1]/'include/os9abi.h').read_text()
    defines = dict(re.findall(r'^#define\s+(\S+)\s+(\S+)', abi, re.M))
    lookup = {key.lower().replace('_','.'):value for key,value in defines.items()}
    def constant(match):
        token=match[0]
        if re.search(r'(?m)^'+re.escape(token)+':',text):return token
        value=lookup.get(token.lower().replace('_','.'))
        seen=set()
        while value in defines and value not in seen:
            seen.add(value);value=defines[value]
        return value.replace('0x','$') if value else token
    defined=set(re.findall(r'(?m)^([A-Za-z_][\w.$]*):',text))
    if not isdefs:text=re.sub(r'\b(?:F\$|I\$|SS[._])[A-Za-z0-9_]+',constant,text,flags=re.I)
    text=re.sub(r'(?mi)(\bequ[ \t]+\S+),(?=[ \t])',r'\1 ;',text)
    public = set(re.findall(r'(?m)^([A-Za-z_][\w$]*):',text))
    constants = {}
    operators = {ast.Add:operator.add, ast.Sub:operator.sub, ast.Mult:operator.mul,
                 ast.BitOr:operator.or_, ast.BitAnd:operator.and_,
                 ast.LShift:operator.lshift, ast.RShift:operator.rshift,
                 ast.USub:operator.neg, ast.UAdd:operator.pos}
    def value(node):
        if isinstance(node,ast.Constant) and type(node.value) is int:return node.value
        if isinstance(node,ast.Name):return constants[node.id]
        if isinstance(node,ast.BinOp):return operators[type(node.op)](value(node.left),value(node.right))
        if isinstance(node,ast.UnaryOp):return operators[type(node.op)](value(node.operand))
        raise ValueError('Not an absolute size')
    def number(expr):
        return value(ast.parse(re.sub(r'\$([0-9a-fA-F]+)',r'0x\1',expr),mode='eval').body)
    for _ in range(8):
        for symbol,expr in re.findall(r'(?mi)^([A-Za-z_]\w*)[ \t]+(?:equ|set)[ \t]+(\S+)',text):
            try:constants[symbol]=number(expr)
            except (KeyError,ValueError,SyntaxError):pass
    def reserve(match):
        try:return match[1]+str(number(match[2]))
        except (KeyError,ValueError,SyntaxError):return match[0]
    text = re.sub(r'(?mi)(\brmb[ \t]+)(\S+)',reserve,text)
    local=set(re.findall(r'(?m)^([A-Za-z_][\w.$]*):?(?=[ \t]|$)',text))
    text=re.sub(r'(?mi)^([ \t]*)(bsr|bra)([ \t]+)([A-Za-z_][\w.$]*)',lambda m:m[1]+('l' if m[4] not in local else '')+m[2]+m[3]+m[4],text)
    adjusted=[]
    for line in text.splitlines():
        parts=line.split()
        opcode=(parts[1] if line and not line[0].isspace() and len(parts)>1 else parts[0] if parts else '').lower()
        if opcode not in ('puls','pulu','pshs','pshu','tfr','exg'):
            line=re.sub(r',pc\b',',pcr',line,flags=re.I)
        line=re.sub(r'^(\s*(?:l?b[a-z]+)\s+)([A-Za-z_][\w.$]*),(?=\s)',r'\1\2 ;',line,flags=re.I)
        adjusted.append(line)
    text='\n'.join(adjusted)+'\n'
    text = text.encode() if isdefs else subprocess.run(['sed','-f',str(Path(c3)/'lwbackend/os9defs.sed')],input=text.encode(),capture_output=True,check=True).stdout
    native = subprocess.run(['awk','-f',str(Path(c3)/'lwbackend/c3lw.awk')],input=text,capture_output=True,check=True).stdout.decode()
    return '\n'.join(line for line in native.splitlines() if not line.startswith('\texport\t') or line.split()[-1] in public)+'\n'


def assembly(path, c3):
    return prepare(expand(path), c3)
