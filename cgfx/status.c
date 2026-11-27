#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
*******************************************
* System Status Functions                 *
* Copyright (c) 1989 by Mike Sweet        *
*******************************************
* Updated for the new C ABI on     *
* 12/31/2005 by tim lindner        *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect status,0,0,0,0,0

* _gs_crsr(path,horpos,verpos)
* int path,*horpos,*verpos;

_gs_crsr:
 pshs y,b
 lbsr _Flush
 puls a
 ldb #SS.Cursr
 bra g0

* _gs_scsz(path,horsiz,versiz)
* int path,*horsiz,*versiz;

_gs_scsz:
 pshs y,b
 lbsr _Flush
 puls a
 ldb #SS.ScSiz
g0
 os9 I$GetStt
 stx [4,s]
 sty [6,s]
 puls y
 bcs os9err0
 clra
 clrb
 rts

* _gs_palt(path,palbuf)
* int path;
* char *palbuf;

_gs_palt:
 pshs y,b
 lbsr _Flush
 puls a
 ldx 4,s
 ldb #SS.Palet
 os9 I$GetStt
 puls y
 bra os9err1

* char *_ss_mgpb(path,grpnum,bufnum,mapflag,size)
* int path,grpnum,bufnum,mapflag,*size;

_ss_mgpb:
 pshs y,b
 lbsr _Flush
 lda 6,s grp num
 ldb 8,s buf num
 tfr d,x
 ldy 9,s map flag
 puls a path
 ldb #SS.MpGPB
 os9 I$SetStt
 sty [10,s] *size
 puls y
 bcc noerr0
 clra
 std errno,y
 clrb
 rts
noerr0 tfr x,d
 rts

* _gs_styp(path,type)
* int path,*type;

_gs_styp: pshs b
 lbsr _Flush
 puls a
 ldb #SS.ScTyp
 os9 I$GetStt
 bcc noerr1

os9err0
 clra
 std errno,y
 ldd #-1
 rts
noerr1 ldx 2,s
 sta 1,x
 clr ,x
 clra
 clrb
 rts

* _gs_fbrg(path,fore,back,bord)
* int path,*fore,*back,*bord;

_gs_fbrg:
 pshs b
 lbsr _Flush
 puls a path
 ldb #SS.FBRgs
 os9 I$GetStt
 bcs os9err0
 stx [6,s] store border reg
 ldx 2,s load fore pointer
 sta 1,x store msb of fore
 clr ,x clear msb of fore
 clra clear msb of back
 std [4,s] store reg in back
 clrb clear return value
 rts

* _ss_gip(path,msres,msport,kbdstrt,kbdrpt)
* int path,msres,msport,kbdstrt,kbdrpt;

_ss_gip:
 pshs y,b
 lda 6,s
 ldb 8,s
 tfr d,x
 lda 10,s
 ldb 12,s
 tfr d,y
 puls a
 ldb #SS.GIP
 os9 I$SetStt
 puls y

os9err1 bcc noerr2
 clra
 std errno,y
 ldd #-1
 rts
noerr2 clra
 clrb
 rts

* _ss_dfpl(path,palbuf)
* int path;
* char *palbuf;

_ss_dfpl:
 ldx 2,s
 tfr b,a
 ldb #SS.DfPal
 os9 I$SetStt
 bra os9err1

* _ss_mtyp(path,montype)
* int path,montype;

_ss_mtyp:
 ldx 2,s
 tfr b,a
 ldb #SS.Montr
 os9 I$SetStt
 bra os9err1

* Modern mapping interface writes both result pointers and returns status.
_cgfx_ss_mgpb:
 pshs y,b
 lbsr _Flush
 lda 6,s
 ldb 8,s
 tfr d,x
 ldy 9,s
 puls a
 ldb #$84
 os9 I$SetStt
 bcs mapped_error
 sty [10,s]
 stx [12,s]
mapped_error puls y
 bra os9err1

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_gs_crsr(path_id path, int *x, int *y)
{
    asm
    {
_Flush	EXTERNAL
		pshs	y
		lbsr	_Flush
		lda		2+2+1,s		get path
		ldb		#SS_Cursr
		bra		g0
	}
}
 
asm error_code
_cgfx_gs_scsz(path_id path, int *x, int *y)
{
    asm
    {
_sysret	EXTERNAL
_os9err	EXTERNAL
		pshs	y
		lbsr 	_Flush
		lda 	2+2+1,s
		ldb 	#SS_ScSiz
g0
		os9 	I$GetStt
		stx 	[2+2+2,s]
		sty 	[2+2+4,s]
		puls 	y
		lbra	_sysret
	}
}

asm error_code
_cgfx_gs_palt(path_id path, char *palbuf)
{
    asm
    {
		pshs 	y
		lbsr 	_Flush
		ldx 	2+2+2,s		get palette buffer pointer
		lda 	2+2+1,s		get path
		ldb 	#SS_Palet
		os9 	I$GetStt
		puls 	y,pc
	}
}

asm error_code
_cgfx_ss_mgpb(path_id path, int grp, int buf, int mapsw, int *size, char *bufaddr)
{
    asm
    {
		pshs 	y
		lbsr 	_Flush
		lda 	2+2+3,s		get group number
		ldb 	2+2+5,s		get buffer number
		tfr 	d,x
		ldy 	2+2+6,s		get mapflag
		lda		2+2+1,s		get path
		ldb 	#SS_MpGPB
		os9 	I$SetStt
		puls 	y
		lbcs	_os9err
		sty 	[2+2+8,s]	save in size pointer
	 	stx		[2+12,s]	save in bufaddr pointer
		lbra	_sysret
	}
}

asm error_code
_cgfx_gs_styp(path_id path, int *type)
{
    asm
    {
		lbsr 	_Flush
		lda 	2+1,s		get path
		ldb 	#SS_ScTyp
		os9 	I$GetStt
		lbcs 	_os9err
		tfr		a,b
		clra
		std		[4,s]
	 	lbra	_sysret
 	}
}

asm error_code
_cgfx_gs_fbrg(path_id path, int *fore, int *back, int *bord)
{
    asm
    {
		lbsr	_Flush
		lda		2+1,s		get path
		ldb		#SS_FBRgs
		os9 	I$GetStt
		lbcs	_os9err
		stx		[2+6,s]		save back
		ldx		2+2,s
		sta		1,x
		clr		,x
		clra
		std		[2+4,s]
		clrb
		rts
	}
}

asm error_code
_cgfx_ss_gip(path_id path, int msres, int msport, int kbdstrt, int kbdrpt)
{
    asm
    {
		pshs 	y
		lda 	2+2+3,s		get msres
		ldb		2+2+5,s		get msport
		tfr		d,x
		lda		2+2+7,s		get kbdstrt
		ldb		2+2+9,s		get kbdrpt
		tfr 	d,y
		lda 	2+2+1,s		get path
		ldb 	#SS_GIP
		os9 	I$SetStt
		puls 	y
		lbra	_sysret
	}
}

asm error_code
_cgfx_ss_dfpl(path_id path, char *palbuf)
{
    asm
    {
		ldx		2+2,s		get palette buffer pointer
		lda		2+1,s		get path
		ldb		#SS_DfPal
		os9 	I$SetStt
os9err1
		lbra	_sysret
	}
}

asm error_code
_cgfx_ss_mtyp(path_id path, int montype)
{
    asm
    {
		ldx		2+2,s		get monitor type
		lda		2+1,s		get path
		ldb		#SS_Montr
		os9 	I$SetStt
		bra 	os9err1
	}
}
#endif
