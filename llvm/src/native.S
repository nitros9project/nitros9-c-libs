/* Compiler-specific callback and process-data helpers. Kernel calls are
 * assembled from the canonical library sources by os9/build.py. */
.text
.globl getsp
getsp:
 leax 2,s
 rts
.globl __cmoc_signal_receiver
__cmoc_signal_receiver:
 tfr u,x
 ldy #24
.Lsave_vregs:
 lda ,x+
 pshs a
 leay -1,y
 bne .Lsave_vregs
 clra
 tfr d,x
 lbsr __cmoc_dispatch_signal
 leax 24,u
 ldy #24
.Lrestore_vregs:
 puls a
 sta ,-x
 leay -1,y
 bne .Lrestore_vregs
 rti
.globl __cmoc_data_base
__cmoc_data_base:
 tfr u,x
 rts
.globl lockdata
lockdata:
 pshs cc
 orcc #0x10
 inc ,x
 beq .Llock_wrapped
 ldb ,x
 dec ,x
 sex
 tfr d,x
 puls cc
 rts
.Llock_wrapped:
 ldx #0
 puls cc
 rts
.globl unlkdata
unlkdata:
 pshs cc
 orcc #0x10
 ldb ,x
 bne .Lunlock_busy
 dec ,x
 ldx #0
 puls cc
 rts
.Lunlock_busy:
 sex
 tfr d,x
 puls cc
 rts
.globl __cmoc_snapshot
__cmoc_snapshot:
 pshs cc,d,dp,x,y,u
 leay ,s
 ldu #10
.Lsnapshot_copy:
 ldb ,y+
 stb ,x+
 leau -1,u
 bne .Lsnapshot_copy
 ldx 4,s
 leay 12,s
 sty 10,x
 puls cc,d,dp,x,y,u
 rts
