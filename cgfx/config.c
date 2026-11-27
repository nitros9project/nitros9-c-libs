#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
******************************************
* Configuration Functions                *
* Copyright (c) 1989 by Mike Sweet       *
******************************************
* Updated to new ABI by tim lindner      *
* December 26, 2005                      *
******************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect config,0,0,0,0,0

PSet:
 lda #$2e
 bra send4

Lset:
LSet:
 lda #$2f
 bra send3

DefColr:
 ldx #$1b30
 pshs x,u
 leax ,s
 tfr b,a
 ldu #2
 lbsr _cgfx_write
 leas 2,s
 bra os9err0

Palette:
 lda #$31
 bra send4

FColor:
 lda #$32
 bra send3

BColor:
 lda #$33
 bra send3

Border:
 lda #$34
 bra send3

ScaleSw:
 lda #$35

******************************************
* Send three bytes to path
******************************************
* B = path number
* First byte is always $1b
* A = second byte to send
* 3,s = third byte to send

send3 exg a,b
 pshs u
 leas -3,s
 stb 1,s
 ldb #$1b
 stb 0,s
 ldb 8,s
 stb 2,s
 ldu #3
 leax ,s
 lbsr _cgfx_write
 leas 3,s
 bra os9err0

SetGC:
 lda #$39

******************************************
* Send four bytes to path
******************************************
* B = path number
* First byte is always $1b
* A = second byte to send
* 3,s = thrid byte to send
* 5,s = third byte to send

send4 exg a,b
 pshs u
 leas -4,s
 stb 1,s
 ldb #$1b
 stb 0,s
 ldb 9,s
 stb 2,s
 ldb 11,s
 stb 3,s
 ldu #4
 leax ,s
 lbsr _cgfx_write
 leas 4,s

os9err0 puls u
 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_pset(path_id path, int grpnum, int bufnum)
{
    asm
    {
_cgfx_write EXTERNAL
        ldd #$1b2e
        bra send4
    }
}

asm error_code
_cgfx_lset(path_id path, int mode)
{
    asm
    {
        ldd #$1b2f
        bra send3
    }
}

asm error_code
_cgfx_defcolr(path_id path)
{
    asm
    {
        ldd #$1b30
        pshs d,u
        leax ,s
        lda 7,s
        ldu #2
        lbsr _cgfx_write
        leas 2,s
        bra os9err0
    }
}

asm error_code
_cgfx_palette(path_id path, int prn, int colno)
{
    asm
    {
        ldd #$1b31
        bra send4
    }
}

asm error_code
_cgfx_fcolor(path_id path, int prn)
{
    asm
    {
        ldd #$1b32
        bra send3
    }
}

asm error_code
_cgfx_bcolor(path_id path, int prn)
{
    asm
    {
        ldd #$1b33
        bra send3
    }
}

asm error_code
_cgfx_border(path_id path, int prn)
{
    asm
    {
        ldd #$1b34
        bra send3
    }
}

asm error_code
_cgfx_scalesw(path_id path, int bsw)
{
    asm
    {
        ldd #$1b35

send3   pshs u
        leas -3,s
        std ,s
        lda 10,s
        sta 2,s
        ldu #3
        leax ,s
        lda 8,s
        lbsr _cgfx_write
        leas 3,s
        bra os9err0
    }
}

asm error_code
_cgfx_setgc(path_id path, int grpnum, int bufnum)
{
    asm
    {
_sysret EXTERNAL
        ldd #$1b39

send4   pshs u
        leas -4,s
        std ,s
        lda 11,s
        ldb 13,s
        std 2,s
        ldu #4
        leax ,s
        lda 9,s
        lbsr _cgfx_write
        leas 4,s

os9err0 puls u
		lbra	_sysret
    }
}

#endif
