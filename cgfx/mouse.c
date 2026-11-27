#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
***************************************
* Mouse Handling Functions            *
* Copyright (c) 1989 by Mike Sweet    *
***************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect mouse,0,0,0,0,0

_ss_mous:
 pshs y,b
 lda 6,s
 ldb 8,s
 tfr d,x
 ldy 9,s
 lda ,s
 ldb #$89
 os9 I$SETSTT
 leas 1,s
 puls y

os9err0 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

_ss_msig:
 ldx 2,s
 tfr b,a
 ldb #$8a
 os9 I$SETSTT
 bra os9err0

_gs_mous:
 pshs y
 ldx 4,s
 tfr b,a
 ldy #0
 ldb #$89
 os9 I$GETSTT
 puls y
 bra os9err0

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_ss_mouse(path_id path, int sample_rate, int timeout, int autofollow)
{
    asm
    {
_sysret	EXTERNAL
		lda		2+2+1,s		get sample rate byte
		ldb		2+2+3,s		get timeout byte
		tfr		d,x
		pshs	y
		ldy		2+2+2+4,s	get autofollow flag
		lda		2+2+1,s		get path
		ldb 	#SS_Mouse
		os9		I$SetStt
		puls	y

os9err0
		lbra	_sysret
	}
}

asm error_code
_cgfx_ss_mssig(path_id path, int signo)
{
    asm
    {
		ldx		2+2,s		get signal number
		lda		2+1,s		get path
		ldb		#SS_MsSig
		os9		I$SetStt
		bra		os9err0
	}
}

asm error_code
_cgfx_gs_mouse(path_id path, MSRET *mpkt)
{
    asm
    {
		pshs 	y
		ldx 	2+2+2,s		get mouse packet pointer
		lda 	2+2+1,s		get path
		ldy 	2+2+4,s		NOT SURE WHAT THIS IS!
		ldb 	#SS_Mouse
		os9 	I$GetStt
		puls	y
		bra 	os9err0
	}
}
#endif
