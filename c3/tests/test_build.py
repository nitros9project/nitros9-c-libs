import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from native_asm import lower
from native_calls import lower as calls
from native_sources import c_view, names
from split_code import split
from build import adapt_data


def spec(args='char *p',result='int'):
    return {'args':args,'return':result}


class SourceTests(unittest.TestCase):
    def test_comments_preserve_urls_and_strings(self):
        self.assertEqual(c_view('char *s="https://example/a/*b*/"; // comment\n'), 'char *s="https://example/a/*b*/"; \n')

    def test_callback_calls_keep_arguments(self):
        source='typedef int (*cmp)(const void *, const void *);\nx=(*compare)(key, middle);'
        view=c_view(source)
        self.assertIn('(*cmp)()',view)
        self.assertIn('(*compare)(key, middle)',view)

    def test_long_api_names_are_distinct(self):
        aliases=names()
        for pair in [('_os_read','_os_readln'),('_os_write','_os_writeln'),('_os_gs_size','_os_gs_scsiz')]:
            self.assertNotEqual(aliases[pair[0]],aliases[pair[1]])
            self.assertTrue(all(len(aliases[n])<=8 for n in pair))

    def test_qualifiers_and_dollar_constants(self):
        self.assertEqual(c_view('const char *p; F$CRC; "const F$CRC";'), ' char *p; F_CRC; "const F$CRC";')


class FrameTests(unittest.TestCase):
    def test_combined_save_has_no_extra_instructions(self):
        source='''_foo:
stk_foo_ret equ 0
stk_foo_p equ 2
 pshs u
 ldx stk_foo_p+2,s
 ldd stk_foo_p+2,s
 puls u,pc
'''
        result,report=lower(source,{'_foo':spec()})
        self.assertEqual(report[0]['mode'],'combined')
        self.assertIn('pshs\td,u',result)
        self.assertIn('puls\tx,u,pc',result)
        self.assertNotIn('leas',result)

    def test_native_long_return_preserves_x(self):
        source='''_foo:
stk_foo_ret equ 0
stk_foo_p equ 2
 pshs u
 ldx stk_foo_p+2,s
 ldd stk_foo_p+2,s
 puls u,pc
'''
        result,_=lower(source,{'_foo':spec(result='long')})
        self.assertIn('puls\td,u,pc',result)

    def test_aliases_select_one_frame(self):
        source='''_foo:
_bar:
stk_foo_ret equ 0
stk_foo_p equ 2
 ldx stk_foo_p,s
 ldd ,x
 rts
'''
        result,report=lower(source,{'_foo':spec(),'_bar':spec()})
        self.assertEqual(len(report),1)
        self.assertNotIn('pshs',result)
        self.assertEqual(result.count('tfr\td,x'),1)

    def test_hoisting_restores_load_flags_at_original_position(self):
        source='''_foo:
stk_foo_ret equ 0
stk_foo_p equ 2
stk_foo_mode equ 4
 lda stk_foo_mode+1,s
 ldx stk_foo_p,s
 beq done
 ldd #1
done rts
'''
        result,_=lower(source,{'_foo':spec('char *p, int mode')})
        self.assertLess(result.index('tfr\td,x'),result.index(' lda '))
        self.assertIn('cmpx\t#0',result)

    def test_conditional_error_discards_argument_local(self):
        source='''_foo:
stk_foo_ret equ 0
stk_foo_path equ 2
stk_foo_path_byte equ 3
 ldb #1
 lda stk_foo_path_byte,s
 os9 $8d
 lblo _os9err
 clra
 rts
'''
        result,_=lower(source,{'_foo':spec('int path')})
        self.assertIn('bhs\t.c3_continue_',result)
        self.assertIn('leas\t2,s',result)
        self.assertIn('puls\tx,pc',result)

    def test_long_by_value_stays_on_stack(self):
        source='_foo:\n ldd 2,s\n rts\n'
        result,report=lower(source,{'_foo':spec('long value')})
        self.assertEqual(result,source)


class CallTests(unittest.TestCase):
    def test_native_call_drops_first_argument_push(self):
        text=' pshs d,x\n lbsr _foo\n leas 4,s\n'
        result,_=calls(text,{'_foo':spec('char *p, int n')},'unit')
        self.assertIn('pshs\tx',result)
        self.assertIn('(4)-2,s',result)
        self.assertNotIn('pshs d,x',result)

    def test_no_foreign_long_destination(self):
        text=' pshs d\n leax _flacc,y\n pshs x\n lbsr _foo\n leas 4,s\n'
        result,_=calls(text,{'_foo':spec('char *p','long')},'unit')
        self.assertNotIn('pshs',result)
        self.assertNotIn('leax',result)
        self.assertIn('(4)-4,s',result)

    def test_unknown_cached_call_fails_closed(self):
        with self.assertRaises(ValueError):calls(' ldd #1\n lbsr _foo\n rts\n',{'_foo':spec('int a, int b')},'unit')


class ArchiveTests(unittest.TestCase):
    def test_function_members_keep_shared_tails_together(self):
        text=''' section code
_a export
_b export
_c export
_a:
 ldd #1
 bra done
_b:
 ldd #2
done rts
_c:
 ldd #3
 rts
 endsect
'''
        members=split(text)
        self.assertEqual(len(members),2)
        self.assertTrue(any('_a:' in m and '_b:' in m for m in members))

    def test_initialized_data_comments_cannot_add_words(self):
        text=' table EXPORT\n section rwdata\ntable\n fdb $3b9a,$ca00 ; two words $3b9a,$ca00\n endsect\n'
        seen=[]
        with patch('build.run',side_effect=lambda cmd,**kw:seen.append(kw['input'].decode()) or b''):
            adapt_data(text,'unit',Path('/unused'))
        self.assertEqual(seen[0].count('$ca00'),1)
        self.assertNotIn('two words',seen[0])


if __name__=='__main__':unittest.main()
