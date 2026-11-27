 IFDEF NITROS9_C3
* C3_RMA_BEGIN
 psect mouse,0,0,0,0,0


 ifp1
* use /dd/defs/os9defs.a
 endc

*************************************************
* Shadow(path,width,length,fg,bg)
* int path,width,length,fg,bg;
*
* Creates an overlay in the center of the current
* window 'width' by 'length'.
*
*
*

Shadow:
 pshs y,b
 lbsr _Flush
 leas -9,s
 lda 9,s
 ldb #SS.SCSIZ
 os9 I$GETSTT
 tfr x,d
 subd 14,s
 lsrb
 stb 3,s
 tfr y,d
 subd 16,s
 lsrb
 stb 4,s
 lda 15,s
 ldb 17,s
 std 5,s
 lda 19,s
 ldb 21,s
 std 7,s
 ldd #$1b22
 std ,s
 lda #1
 sta 2,s
 leax ,s
 ldy 10,s
 stu 10,s
 ldu #9
 lda 9,s
 lbsr _cgfx_write
 bcc noerror
 clra
 std errno,y
 ldd #-1
 bra srts
noerror clra
 clrb
srts leas 10,s
 puls u,pc


 endsect


* C3_RMA_END
 ELSE
        section code

__cgfx_shadow           EXPORT * export this symbol (cmoc mangles C `_cgfx_shadow` to asm `__cgfx_shadow`)

_errno                  EXTERNAL * import external symbol
_Flush                  EXTERNAL * import external symbol
_cgfx_write             EXTERNAL * import external symbol

* Create a centered overlay shadow box: _cgfx_shadow(path,width,length,fg,bg)
__cgfx_shadow
        pshs    y
        lbsr    _Flush * long branch to subroutine to _Flush
        leas    -9,s * adjust S using -9,s
        lda     14,s * load A from stack-relative value 14,s
        ldb     #$26 * load B from immediate value $26
        os9     $8D * invoke OS-9 system call $8D
        tfr     x,d
        subd    15,s * subtract stack-relative value 15,s from D
        lsrb * logical shift B right by one bit
        stb     3,s * store B to stack-relative value 3,s
        tfr     y,d
        subd    17,s * subtract stack-relative value 17,s from D
        lsrb * logical shift B right by one bit
        stb     4,s * store B to stack-relative value 4,s
        lda     16,s * load A from stack-relative value 16,s
        ldb     18,s * load B from stack-relative value 18,s
        std     5,s * store D to stack-relative value 5,s
        lda     20,s * load A from stack-relative value 20,s
        ldb     22,s * load B from stack-relative value 22,s
        std     7,s * store D to stack-relative value 7,s
        ldd     #$1b22 * load D from immediate value $1b22
        std     ,s * store D to memory pointed to by S
        lda     #1 * load A from immediate value 1
        sta     2,s * store A to stack-relative value 2,s
        leax    ,s * compute effective address into X from ,s
        ldu     #9 * load U from immediate value 9
        lda     14,s * load A from stack-relative value 14,s
        lbsr    _cgfx_write * long branch to subroutine to _cgfx_write
        bcc     noerror
        clra * clear A
        std     _errno,y * store D to indexed value _errno,y
        ldd     #-1 * load D from immediate value -1
        bra     srts
noerror clra * clear A
        clrb * clear B
srts    leas    9,s * adjust S using 9,s
        puls    u,pc

        endsect * end current section

 ENDC
