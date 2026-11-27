#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
***************************************
* Standard Windowing Functions (MW C) *
* Copyright (c) 1989 by Mike Sweet    *
***************************************
* Updated for the new C ABI on     *
* 12/31/2005 by tim lindner        *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect window,0,0,0,0,0

* int DWSet(path,sty,cpx,cpy,szx,szy,fprn,bprn,bdprn)
* int path,sty,cpx,cpy,szx,szy,fprn,bprn,bdprn;

DWSet:
 pshs y,b
 lbsr _Flush
 leas -10,s
 ldy #10
 ldd #$1b20
 std ,s
 lda 16,s
 bne d0
 leay -1,y
d0 ldb 18,s
 std 2,s
 lda 20,s
 ldb 22,s
 std 4,s
 lda 24,s
 ldb 26,s
 std 6,s
 lda 28,s
 ldb 30,s
 std 8,s
 lda 10,s
 leax ,s
 os9 I$Write
 leas 11,s buffer, plus reg b
 bra os9err0

* int DWEnd(path)
* int path;

DWEnd:
 pshs y,b
 lbsr _Flush
 ldd #$1b24
 pshs d
 leax ,s
 ldy #2
 lda 2,s
 os9 I$Write
 leas 3,s buffer, plus reg b
 bra os9err0

* int DWProtSw(path,bsw)
* int path,bsw;

DWProtSw:
 pshs y,b
 lbsr _Flush
 lda 6,s
 pshs a
 ldd #$1b36
 pshs d
 lda 4,s
 ldy #3
 leax ,s
 os9 I$Write
 leas 4,s buffer, plus reg b

os9err0 puls y
 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

* int OWSet(path,svs,cpx,cpy,szx,szy,fprn,bprn)
* int path,svs,cpx,cpy,szx,szy,fprn,bprn;

OWSet:
 pshs y,b
 lbsr _Flush
 leas -9,s
 lda 15,s
 ldb 17,s
 std 2,s
 lda 19,s
 ldb 21,s
 std 4,s
 lda 23,s
 ldb 25,s
 std 6,s
 lda 27,s
 sta 8,s
 ldd #$1b22
 std ,s
 ldy #9
 leax ,s
 lda 9,s
 os9 I$Write
 leas 10,s buffer, plus reg b
 bra os9err0

* int MVOWEnd(path)
* int path;

MVOWEnd:
 pshs y,b
 lbsr _Flush
 lda 0,s
 ldb #$86 first _ss_wset the overlay to no box...
 ldy #0
 os9 I$SetStt
 bra o0 then do OWEnd....

* int UnShadow(path)
* int path;

* int OWEnd(path)
* int path;

UnShadow:
OWEnd:
 pshs y,b
 lbsr _Flush
o0 ldd #$1b23
 pshs d
 lda 2,s
 ldy #2
 leax ,s
 os9 I$Write
 leas 3,s buffer, plus reg b
 bra os9err0

* int Select(path)
* int path;

Select:
 pshs y,b
 lbsr _Flush
 ldd #$1b21
 pshs d
 leax ,s
 lda 2,s
 ldy #2
 os9 I$Write
 leas 3,s buffer, plus reg b
 lbra os9err0

* int CWArea(path,cpx,cpy,szx,szy);
* int path,cpx,cpy,szx,szy;

CWArea:
 pshs y,b
 lbsr _Flush
 leas -6,s
 lda 12,s
 ldb 14,s
 std 2,s
 lda 16,s
 ldb 18,s
 std 4,s
 ldd #$1b25
 std ,s
 lda 6,s
 ldy #6
 leax ,s
 os9 I$Write
 leas 7,s buffer, plus reg b
 lbra os9err0

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

/***************************************
 * Standard Windowing Functions (MW C) *
 * Copyright (c) 1989 by Mike Sweet    *
 ***************************************/

asm error_code
_cgfx_dwset(path_id path, int sty, int cpx, int cpy, int szx, int szy, int fprn, int bprn, int bdprn)
{
	asm
	{
_Flush EXTERNAL
        pshs y
        lbsr _Flush
        leas -10,s
        ldy #10
        ldd #$1b20
        std ,s
        lda 17,s
        bne d0
        leay -1,y
d0      ldb 19,s
        std 2,s
        lda 21,s
        ldb 23,s
        std 4,s
        lda 25,s
        ldb 27,s
        std 6,s
        lda 29,s
        ldb 31,s
        std 8,s
        lda 15,s
        leax ,s
        os9 I$Write
        leas 10,s
        bra os9err0
    }
}

asm error_code
_cgfx_dwend(path_id path)
{
	asm
	{
        lbsr _Flush
        pshs y
        ldd #$1b24
        pshs d
        leax ,s
        ldy #2
        lda 7,s
        os9 I$Write
        leas 2,s
        bra os9err0
    }
}

asm error_code
_cgfx_dwprotsw(path_id path, int bsw)
{
	asm
	{
_sysret	EXTERNAL
        pshs y
        lbsr _Flush
        lda 7,s
        pshs a
        ldd #$1b36
        pshs d
        lda 8,s
        ldy #3
        leax ,s
        os9 I$Write
        leas 3,s
os9err0 puls y
		lbra	_sysret
    }
}

asm error_code
_cgfx_owset(path_id path, int svs, int cpx, int cpy, int szx, int szy, int fprn, int bprn)
{
	asm
	{
        pshs y
        lbsr _Flush
        leas -9,s
        lda 16,s
        ldb 18,s
        std 2,s
        lda 20,s
        ldb 22,s
        std 4,s
        lda 24,s
        ldb 26,s
        std 6,s
        lda 28,s
        sta 8,s
        ldd #$1b22
        std ,s
        ldy #9
        leax ,s
        lda 14,s
        os9 I$Write
        leas 9,s
        lbra os9err0
    }
}

asm error_code
_cgfx_mvowend(path_id path)
{
	asm
	{
        pshs y
        lbsr _Flush
        lda 5,s
        ldb #$86 first _ss_wset the overlay to no box...
        ldy #0
        os9 I$SetStt
        bra o0 then do OWEnd....
     }
}

asm error_code
_cgfx_owend(path_id path)
{
	asm
	{
        pshs y
        lbsr _Flush
o0      ldd #$1b23
        pshs d
        lda 7,s
        ldy #2
        leax ,s
        os9 I$Write
        leas 2,s
        lbra os9err0
    }
}

asm error_code
_cgfx_select(path_id path)
{
	asm
	{
        pshs y
        lbsr _Flush
        ldd #$1b21
        pshs d
        leax ,s
        lda 7,s
        ldy #2
        os9 I$Write
        leas 2,s
        lbra os9err0
    }
}        

asm error_code
_cgfx_cwarea(path_id path, int cpx, int cpy, int szx, int szy)
{
	asm
	{
        pshs y
        lbsr _Flush
        leas -6,s
        lda 13,s
        ldb 15,s
        std 2,s
        lda 17,s
        ldb 19,s
        std 4,s
        ldd #$1b25
        std ,s
        lda 11,s
        ldy #6
        leax ,s
        os9 I$Write
        leas 6,s
        lbra os9err0
    }
}

#endif
