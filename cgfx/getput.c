#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
************************************
* Get/Put Functions                *
* Copyright (c) 1989 by Mike Sweet *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect getput,0,0,0,0,0

DfnGPBuf:
 pshs u,b
 leas -6,s
 ldu #6
 ldd #$1b29
 std ,s
 lda 12,s
 ldb 14,s
 std 2,s
 ldd 15,s
 std 4,s
 lda 6,s
 leax ,s
 lbsr _cgfx_write
 leas 6,s
 bra os9err0

KilBuf:
 pshs u,b
 lda 6,s
 ldb 8,s
 pshs d
 ldd #$1b2a
 pshs d
 lda 4,s
 ldu #4
 leax ,s
 lbsr _cgfx_write
 leas 4,s
 bra os9err0

GPLoad:
 pshs u,b
 leas -11,s
 lda 17,s
 ldb 19,s
 std 2,s
 lda 21,s
 sta 4,s
 ldd 22,s
 std 5,s
 ldd 24,s
 std 7,s
 ldd 26,s
 std 9,s
 ldd #$1b2b
 std ,s
 leax ,s
 ldu #11
 lda 11,s
 lbsr _cgfx_write
 leas 11,s

os9err0 leas 1,s
 puls u
 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

GetBlk:
 pshs u,b
 leas -12,s
 lda 18,s
 ldb 20,s
 std 2,s
 ldd 21,s
 std 4,s
 ldd 23,s
 std 6,s
 ldd 25,s
 std 8,s
 ldd 27,s
 std 10,s
 ldd #$1b2c
 std ,s
 leax ,s
 ldu #12
 lda 12,s
 lbsr _cgfx_write
 leas 12,s
 bra os9err0

PutBlk:
 pshs u,b
 leas -8,s
 lda 14,s
 ldb 16,s
 std 2,s
 ldd 17,s
 std 4,s
 ldd 19,s
 std 6,s
 ldd #$1b2d
 std ,s
 leax ,s
 ldu #8
 lda 8,s
 lbsr _cgfx_write
 leas 8,s
 bra os9err0

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_dfngpbuf(path_id path, int grp, int buf, int bl)
{
    asm
    {
_cgfx_write	EXTERNAL
		pshs u
		leas -6,s
		ldu #6
		ldd #$1b29
		std ,s
		lda 8+2+2+1,s		get group number
		ldb 8+2+2+3,s		get buffer number
		std 2,s
		ldd 8+2+2+4,s		get buffer length
		std 4,s
		lda 8+2+1,s			get path
		leax ,s
		lbsr _cgfx_write
		leas 6,s
		bra os9err0
	}
}

asm error_code
_cgfx_kilbuf(path_id path, int grp, int buf)
{
    asm
    {
		pshs u
		lda 2+2+3,s		get group number
		ldb 2+2+5,s		get buffer number
		pshs d
		ldd #$1b2a
		pshs d
		lda 6+2+1,s		get path
		ldu #4
		leax ,s
		lbsr _cgfx_write
		leas 4,s
		bra os9err0
	}
}

asm error_code
_cgfx_gpload(path_id path, int grp, int buf, int sty, int sx, int sy, int bl)
{
    asm
    {
_sysret	EXTERNAL
		pshs u
		leas -11,s
		lda 11+2+2+3,s		get group number
		ldb 11+2+2+5,s		get buffer number
		std 2,s
		lda 11+2+2+7,s		get sty
		sta 4,s
		ldd 11+2+2+8,s		get sx
		std 5,s
		ldd 11+2+2+10,s		get sy
		std 7,s
		ldd 11+2+2+12,s		get buffer length
		std 9,s
		ldd #$1b2b
		std ,s
		leax ,s
		ldu #11
		lda 16,s
		lbsr _cgfx_write
		leas 11,s
os9err0 puls u
		lbra	_sysret
	}
}

asm error_code
_cgfx_getblk(path_id path, int grp, int buf, int bx, int by, int sx, int sy)
{
    asm
    {
		pshs u
		leas -12,s
		lda 12+2+2+3,s		get group number
		ldb 12+2+2+5,s		get buffer number
		std 2,s
		ldd 12+2+2+6,s		get bx
		std 4,s
		ldd 12+2+2+8,s		get by
		std 6,s
		ldd 12+2+2+10,s		get sx
		std 8,s
		ldd 12+2+2+12,s		get sy
		std 10,s
		ldd #$1b2c
		std ,s
		leax ,s
		ldu #12
		lda 17,s
		lbsr _cgfx_write
		leas 12,s
		bra os9err0
	}
}

asm error_code
_cgfx_putblk(path_id path, int grp, int buf, int bx, int by)
{
    asm
    {
		pshs u
		leas -8,s
		lda 8+2+2+3,s		get group number
		ldb 8+2+2+5,s		get buffer number
		std 2,s
		ldd 8+2+2+6,s		get bx
		std 4,s
		ldd 8+2+2+8,s		get by
		std 6,s
		ldd #$1b2d
		std ,s
		leax ,s
		ldu #8
		lda 13,s
		lbsr _cgfx_write
		leas 8,s
		bra os9err0
	}
}#endif
