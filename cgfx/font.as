 IFDEF NITROS9_C3
* C3_RMA_BEGIN
************************************
* Font Handling Functions          *
* Copyright (c) 1989 by Mike Sweet *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect font,0,0,0,0,0

* int Font(path,grpnum,bufnum)
* int path,grpnum,bufnum;

Font:
 pshs u,b
 lda 6,s
 ldb 8,s
 pshs d
 ldd #$1b3a
 pshs d
 ldu #4
 leax ,s
 lda 4,s
 lbsr _cgfx_write
 leas 5,s
 bra os9err0

* int TCharSw(path,bsw)
* int path,bsw;

TCharSw:
 ldx #$1b3c
 bra send3

* int BoldSw(path,bsw)
* int path,bsw;

BoldSw:
 ldx #$1b3d
 bra send3

* int PropSw(path,bsw)
* int path,bsw;

PropSw:
 ldx #$1b3f

send3 pshs u
 leas -3,s
 stx ,s
 lda 8,s
 sta 2,s
 ldu #3
 leax ,s
 tfr b,a
 lbsr _cgfx_write
 leas 3,s

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
 ELSE
        section code

__cgfx_font              EXPORT * export this symbol
__cgfx_tcharsw           EXPORT * export this symbol
__cgfx_boldsw            EXPORT * export this symbol
__cgfx_propsw            EXPORT * export this symbol

_errno                   EXTERNAL * import external symbol
_cgfx_write                  EXTERNAL * import external symbol

* Set the active font: _cgfx_font(path, grp, buf)
__cgfx_font
        pshs    u
        lda     7,s * load A from stack-relative value 7,s
        ldb     9,s * load B from stack-relative value 9,s
        pshs    d
        ldd     #$1b3a * load D from immediate value $1b3a
        pshs    d
        ldu     #4 * load U from immediate value 4
        leax    ,s * compute effective address into X from ,s
        lda     9,s * load A from stack-relative value 9,s
        lbsr    _cgfx_write * long branch to subroutine to _cgfx_write
        leas    4,s * adjust S using 4,s
        bra     os9err0

* Transparent character switch: _cgfx_tcharsw(path, sw)
__cgfx_tcharsw
        ldd     #$1b3c * load D from immediate value $1b3c
        bra     send3

* Bold switch: _cgfx_boldsw(path, sw)
__cgfx_boldsw
        ldd     #$1b3d * load D from immediate value $1b3d
        bra     send3

* Proportional-width switch: _cgfx_propsw(path, sw)
__cgfx_propsw
        ldd     #$1b3f * load D from immediate value $1b3f

send3   pshs    u * save U on the hardware stack
        leas    -3,s * adjust S using -3,s
        std     ,s * store D to memory pointed to by S
        lda     10,s * load A from stack-relative value 10,s
        sta     2,s * store A to stack-relative value 2,s
        ldu     #3 * load U from immediate value 3
        leax    ,s * compute effective address into X from ,s
        lda     8,s * load A from stack-relative value 8,s
        lbsr    _cgfx_write * long branch to subroutine to _cgfx_write
        leas    3,s * adjust S using 3,s

os9err0 puls    u * restore U from the hardware stack
        bcc     noerr0
        clra * clear A
        std     _errno,y * store D to indexed value _errno,y
        ldd     #-1 * load D from immediate value -1
        rts * return to caller
noerr0  clra * clear A
        clrb * clear B
        rts * return to caller

        endsect * end current section

 ENDC
