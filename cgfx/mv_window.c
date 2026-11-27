#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
***************************************
* Multi-Vue Windowing Functions       *
* Copyright (c) 1989 by Mike Sweet    *
***************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect mv_window,0,0,0,0,0

_ss_wset:
 pshs y,b
 lbsr _Flush
 lda ,s
 ldb #$86
 ldx 7,s
 ldy 5,s
 os9 I$SETSTT
 leas 1,s
 puls y
 bra os9err0

_gs_msel:
 tfr b,a
 ldb #$87
 os9 I$GETSTT
 bcs os9err0
 pshs a
 clra
 std [3,s]
 puls b,pc

_ss_umbar:
_ss_umba:
 tfr b,a
 ldb #$95
 os9 I$SETSTT

os9err0 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

_ss_sbar:
 pshs y
 tfr b,a
 ldx 4,s
 ldy 6,s
 ldb #$88
 os9 I$SETSTT
 puls y
 bra os9err0

* Native modern interface returns status and writes both result pointers.
_cgfx_gs_mnsel:
 tfr b,a
 ldb #$87
 os9 I$GETSTT
 bcs os9err0
 pshs a
 clra
 std [3,s]
 puls b
 std [4,s]
 clrb
 rts

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_ss_wnset(path_id path, int wintype, WNDSCR *windat)
{
    asm
    {
_Flush	EXTERNAL
_sysret	EXTERNAL
		pshs	y
		lbsr	_Flush
		lda		2+2+1,s			get path
		ldb		#SS_WnSet
		ldx		2+2+4,s			get WNDSCR ptr
		ldy		2+2+2,s			get window type
		os9		I$SetStt
		puls	y
		bra		os9err0
	}
}

asm error_code
_cgfx_gs_mnsel(path_id path, int *itemno, int *menuid)
{
    asm
    {
		lda		2+1,s			get path
		ldb		#SS_MnSel
		os9		I$GetStt
		bcs		os9err0
		pshs	a
		clra
		std		[2+1+2,s]		save into item no pointer
		puls	b
		std		[2+4,s]			save into menu id pointer
		lbra	_sysret
	}
}

asm error_code
_cgfx_ss_umbar(path_id path)
{
    asm
    {
_sysret	EXTERNAL
		lda		2+1,s			get path
		ldb		#SS_UMBar
		os9		I$SetStt
os9err0	lbra	_sysret
	}
}

asm error_code
_cgfx_ss_sbar(path_id path, int horbar, int verbar)
{
    asm
    {
		pshs	y
		lda		2+2+1,s		get path
		ldx		2+2+2,s		get horizontal bar
		ldy		2+2+4,s		get veritcal bar
		ldb		#SS_SBar
		os9		I$SetStt
		puls	y
		bra 	os9err0
	}
}

#endif
