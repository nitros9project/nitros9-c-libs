#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
*****************************************
* Drawing Functions                     *
* Copyright (c) 1989 by Mike Sweet      *
*****************************************
* Updated for the new C ABI on          *
* 12/27/2005 by tim lindner             *
*****************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect draw,0,0,0,0,0

SetDPtr:
 ldx #$1b40
 bra send6

RSetDPtr:
 ldx #$1b41
 bra send6

Point:
 ldx #$1b42
 bra send6

RPoint:
 ldx #$1b43
 bra send6

Line:
 ldx #$1b44
 bra send6

RLine:
 ldx #$1b45
 bra send6

LineM:
 ldx #$1b46
 bra send6

RLineM:
 ldx #$1b47
 bra send6

Box:
 ldx #$1b48
 bra send6

RBox:
 ldx #$1b49
 bra send6

Bar:
 ldx #$1b4a
 bra send6

RBar:
 ldx #$1b4b
 bra send6

FFill:
 ldx #$1b4f

send2 pshs u,x
 tfr b,a
 leax ,s
 ldu #2
 lbsr _cgfx_write
 leas 2,s
 bra os9err0

Circle:
 pshs u
 ldx 4,s
 pshs x
 ldx #$1b50
 pshs x
 tfr b,a
 leax ,s
 ldu #4
 lbsr _cgfx_write
 leas 4,s
 bra os9err0

Ellipse:
 ldx #$1b51
 bra send6

PutGC:
 ldx #$1b4e

send6 pshs u
 leas -6,s
 stx ,s
 ldx 10,s
 stx 2,s
 ldx 12,s
 stx 4,s
 tfr b,a
 leax ,s
 ldu #6
 lbsr _cgfx_write
 leas 6,s

os9err0 puls u
 bcc noerr0
 clra
 std errno,y
 ldd #-1
 rts
noerr0 clra
 clrb
 rts

Arc:
 pshs u save u
 ldx 2,s load return address
 pshs x stack it
 leax 4,s load start of buffer address
 ldu #$1b52 arc command
 tfr b,a path into a
 stu ,x store arc command
 ldu #14 buffer length
 lbsr _cgfx_write write it
 puls x get return address
 stx 2,s put it back
 bra os9err0

 endsect

* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_setdptr(path_id path, int x, int y)
{
    asm
    {
_cgfx_write EXTERNAL
        ldd #$1b40
        bra send6
    }
}

asm error_code
_cgfx_rsetdptr(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b41
        bra send6
    }
}

asm error_code
_cgfx_point(path_id path, int x, int y)
{
    asm
    {
        ldd #$1b42
        bra send6
    }
}

asm error_code
_cgfx_rpoint(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b43
        bra send6
    }
}

asm error_code
_cgfx_line(path_id path, int x, int y)
{
    asm
    {
        ldd #$1b44
        bra send6
    }
}

asm error_code
_cgfx_rline(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b45
        bra send6
    }
}

asm error_code
_cgfx_linem(path_id path, int x, int y)
{
    asm
    {
        ldd #$1b46
        bra send6
    }
}

asm error_code
_cgfx_rlinem(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b47
        bra send6
    }
}

asm error_code
_cgfx_box(path_id path, int x, int y)
{
    asm
    {
        ldd #$1b48
        bra send6
    }
}

asm error_code
_cgfx_rbox(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b49
        bra send6
    }
}

asm error_code
_cgfx_bar(path_id path, int x, int y)
{
    asm
    {
        ldd #$1b4a
        bra send6
    }
}

asm error_code
_cgfx_rbar(path_id path, int xo, int yo)
{
    asm
    {
        ldd #$1b4b
        bra send6
    }
}

asm error_code
_cgfx_ffill(path_id path)
{
    asm
    {
        ldd #$1b4f

send2   pshs u,d
        lda 7,s
        leax ,s
        ldu #2
        lbsr _cgfx_write
        leas 2,s
        bra os9err0
    }
}

asm error_code
_cgfx_circle(path_id path, int radius)
{
    asm
    {
        pshs u
        ldd 6,s
        pshs d
        ldd #$1b50
        pshs d
        lda 9,s
        leax ,s
        ldu #4
        lbsr _cgfx_write
        leas 4,s
        bra os9err0
    }
}

asm error_code
_cgfx_ellipse(path_id path, int xrad, int yrad)
{
    asm
    {
        ldd #$1b51
        bra send6
    }
}

asm error_code
_cgfx_putgc(path_id path, int x, int y)
{
    asm
    {
_sysret EXTERNAL
        ldd #$1b4e

send6   pshs u
        leas -6,s
        std ,s
        ldd 12,s
        std 2,s
        ldd 14,s
        std 4,s
        lda 11,s
        leax ,s
        ldu #6
        lbsr _cgfx_write
        leas 6,s

os9err0 puls u
		lbra	_sysret
    }
}

asm error_code
_cgfx_arc(path_id path, int xrad, int yrad, int xo1, int yo1, int xo2, int yo2)
{
    asm
    {
        pshs u
        leax 4,s
        ldu #$1b52
        lda 5,s
        stu ,x
        ldu #14
        lbsr _cgfx_write
        bra os9err0
    }
}

#endif
