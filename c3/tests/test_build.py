import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from native_asm import lower
from native_calls import lower as calls
from native_sources import c_view, names
from split_code import split
from build import adapt_data, optimize_rma
from private_stdio import select as private_stdio
from profiles import select as profile
from size_report import measure, compare


def spec(args='char *p',result='int'):
    return {'args':args,'return':result}


class SourceTests(unittest.TestCase):
    def test_stdio_does_not_inject_nonstandard_boolean_macros(self):
        result=c_view('#define TRUE (1)\n#define FALSE (0)\n#define EOF -1\n',header=True)
        self.assertNotIn('TRUE',result)
        self.assertNotIn('FALSE',result)
        self.assertIn('#define EOF -1',result)

    def test_signal_header_exposes_word_handler_result_to_c3(self):
        source='typedef void (*sighandler_t)(int);\n#define SIG_IGN ((sighandler_t) 1)\nsighandler_t signal(int signo, sighandler_t handler);\n'
        result=c_view(source,header=True)
        self.assertIn('int signal();',result)
        self.assertIn('#define SIG_IGN 1',result)
        self.assertNotIn('sighandler_t signal',result)

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
    def test_saved_pointer_returns_directly_in_d(self):
        source='_foo:\nstk_foo_ret equ 0\nstk_foo_p equ 2\n pshs u\n ldu stk_foo_p+2,s\ndone ldd stk_foo_p+2,s\n puls u,pc\n'
        result,_=lower(source,{'_foo':spec(result='char *')},name='strings')
        self.assertNotIn('ldd',result)
        self.assertIn('done:',result)
        self.assertIn('puls\td,u,pc',result)

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
        self.assertIn('puls\td,u,pc',result)
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
    def test_local_calls_link_independent_archive_members(self):
        source=' section code\n_a export\n_b export\n_a:\n lbsr helper\n rts\n_b:\n ldd #2\n rts\nhelper:\n ldd #1\n rts\n endsect\n'
        members=split(source)
        self.assertEqual(len(members),3)
        caller=next(m for m in members if '_a:' in m)
        callee=next(m for m in members if 'helper:' in m)
        self.assertIn('helper EXTERNAL',caller)
        self.assertIn('helper EXPORT',callee)
        self.assertNotIn('_b:',caller)
        self.assertNotIn('_a:',callee)

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


    def test_separate_initialized_sections_have_distinct_image_names(self):
        text=' section rwdata\na fdb 1\n endsect\n section rwdata\nb fdb 2\n endsect\n'
        seen=[]
        with patch('build.run',side_effect=lambda cmd,**kw:seen.append(kw['input'].decode()) or b''):
            adapt_data(text,'unit',Path('/unused'))
        self.assertEqual(len(seen),2)
        self.assertNotEqual(seen[0].splitlines()[0],seen[1].splitlines()[0])


class OverheadTests(unittest.TestCase):
    def test_data_only_units_skip_code_optimizer(self):
        source=b' psect data,0,0,0,0,0\n vsect\na rmb 2\n endsect\n endsect\n'
        with patch('build.run') as run:
            self.assertEqual(optimize_rma(source,'data','optx'),source)
            run.assert_not_called()

    def test_independent_ctype_functions_are_optimized_separately(self):
        source=b' psect unit,0,0,0,0,0\n ttl a\na: rts\n ttl b\nb: rts\n endsect\n'
        seen=[]
        with patch('build.run',side_effect=lambda cmd,**kw:seen.append(kw['input']) or kw['input']):
            optimize_rma(source,'ctypefn','optx')
        self.assertEqual(len(seen),2)
        self.assertTrue(all(x.count(b' ttl ')==1 for x in seen))

    def test_private_file_helper_preserves_shared_success_and_failure(self):
        source='_flush:\n pshs u\n ldu stk_flush_file+2,s\n leas -4,s\n tst ,u\n beq bad\n clra\n clrb\n bra done\nbad ldd #-1\ndone leas 4,s\n puls u,pc\n'
        result=private_stdio(source,'fflush')
        self.assertNotIn('pshs',result)
        self.assertNotIn('ldu',result)
        self.assertIn('ldd #-1',result)
        self.assertIn('leas 4,s',result)
        self.assertIn('rts',result)

    def test_private_file_call_keeps_cleanup_label(self):
        result=private_stdio(' pshs u\n lbsr _flush\nafter std ,s++\n bne failed\n','putc')
        self.assertNotIn('pshs',result)
        self.assertIn('after:',result)
        self.assertIn('bne failed',result)
        with self.assertRaises(ValueError):private_stdio(' pshs x\n lbsr _flush\n leas 2,s\n','unit')

    def test_native_long_call_keeps_returned_accumulator(self):
        source=' leax _flacc,y\n pshs x,u\n lbsr _foo\n leas 4,s\nafter leax _flacc,y\n ldd 2,x\n'
        result,_=calls(source,{'_foo':spec('char *p','long')},'unit')
        self.assertNotIn('leax',result)
        self.assertIn('after:',result)
        self.assertIn('ldd 2,x',result)

    def test_long_self_copy_is_removed_but_result_pointer_remains(self):
        source=' leax _flacc,y\n ldd _flacc,y\n std 0,x\n ldd _flacc+2,y\n std 2,x\n rts\n'
        result=profile(source,'io')
        self.assertIn('leax _flacc,y',result)
        self.assertNotIn('std',result)
        self.assertNotIn('ldd',result)


class SizeAccountingTests(unittest.TestCase):
    @staticmethod
    def module(code_bytes):
        header=bytearray(13)
        header[:2]=b'\x87\xcd'
        header[2:4]=(13+code_bytes+5+3).to_bytes(2,'big')
        header[4:6]=(13+code_bytes).to_bytes(2,'big')
        return bytes(header)+bytes(code_bytes)+b'prob\xe5'+bytes(3)

    def test_bss_does_not_count_as_module_bytes(self):
        text='Section: code (/tmp/unit.o) load at 000D, length 000A\nSection: bss (/tmp/unit.o) load at 0000, length 1000\n'
        result=measure(text,self.module(10))
        self.assertEqual(result['loaded_bytes'],10)
        self.assertEqual(result['overhead_bytes'],21)

    def test_unaccounted_loaded_bytes_are_rejected(self):
        text='Section: code (/tmp/unit.o) load at 000D, length 0009\n'
        with self.assertRaises(ValueError):measure(text,self.module(10))

    def test_deltas_reconcile_to_complete_module_length(self):
        old=measure('Section: code (/tmp/unit.o) load at 000D, length 000A\n',self.module(10))
        new=measure('Section: code (/tmp/unit.o) load at 000D, length 000C\n',self.module(12))
        result=compare(old,new)
        self.assertEqual(result['delta'],2)
        self.assertEqual(sum(row['delta'] for row in result['members']),2)


if __name__=='__main__':unittest.main()
