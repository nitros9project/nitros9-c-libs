"""Check native assembly selection, aliases, and error/data relocation."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'os9'))
from build import generate, select_llvm_inputs


class AssemblySelectionTests(unittest.TestCase):
    def test_pointer_argument_has_no_bridge_or_redundant_moves(self):
        text = ''' section code
__os_getime EXPORT
__os_getime:
stk_time_ret equ 0
stk_time_p equ 2
 ldx stk_time_p,s
 os9 21
 lbra _osret
 endsect
'''
        output = ''.join(generate(text, 'time'))
        self.assertNotIn('tfr x,d', output)
        self.assertNotIn('tfr d,x', output)
        self.assertIn('os9 21', output)
        self.assertNotIn('lbsr', output)
        self.assertIn('.set cmoc_os_getime, _os_getime', output)

    def test_dp_save_is_not_mistaken_for_a_d_argument_save(self):
        text = """ section code
__os_close EXPORT
__os_close:
stk_close_ret equ 0
stk_close_path equ 2
 pshs dp,y,u
 lda stk_close_path+6,s
 os9 143
 puls dp,y,u
 lbra _osret
 endsect
"""
        output = ''.join(generate(text, 'io'))
        self.assertIn('pshs dp,y,u', output)
        self.assertNotIn('pshs xp', output)

    def test_native_input_survives_a_chain_frame_without_extra_moves(self):
        text = '\ttfr x,d /* native LLVM first argument */\n\ttfr u,y\n\tleau ,s\n\tleas 255,y\n\ttfr d,x\n'
        output = select_llvm_inputs(text)
        self.assertNotIn('tfr x,d', output)
        self.assertNotIn('tfr d,x', output)
        self.assertIn('tfr u,y', output)

    def test_pointer_null_flags_follow_the_native_x_value(self):
        text = '\ttfr x,d /* native LLVM first argument */\n\tpshs y\n\ttfr d,x\n\tcmpd #0\n'
        output = select_llvm_inputs(text)
        self.assertIn('cmpx #0', output)
        self.assertNotIn('cmpd', output)

    def test_error_store_uses_llvm_data_relocation(self):
        text = ''' section code
_oserr EXPORT
_oserr:
 clra
 std _errno,y
 rts
 endsect
'''
        output = ''.join(generate(text, 'syscommon'))
        self.assertIn('mc6809_os9_data(errno),u', output)
        self.assertIn('tfr d,x', output)
        self.assertNotIn('errno,y', output)

    def test_first_scalar_uses_x_and_returns_in_x(self):
        text = ''' section code
__os_wait EXPORT
__os_wait:
stk_wait_ret equ 0
stk_wait_out equ 2
 pshs y
 ldx stk_wait_out+2,s
 ldd #7
 std ,x
 puls y,pc
 endsect
'''
        output = ''.join(generate(text, 'process'))
        self.assertIn('tfr d,x', output)
        self.assertNotIn('lbsr', output)


if __name__ == '__main__':
    unittest.main()
