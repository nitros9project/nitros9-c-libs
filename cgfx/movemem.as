 IFDEF NITROS9_C3
* C3_RMA_BEGIN
***************************************************************
* 'movemem.a' - memory moving functions for OS-9/6809.
* by Mike Sweet 3/21/90
*
************************************
* Updated for the new C ABI on     *
* 12/27/2005 by tim lindner        *
************************************
*
* movemem(d,s,bytes)
* char *d,*s;
* int bytes;
*
* 'movemem()' wil copy the data at 's' to 'd', taking
* into account any overlap that might exist.
*

 psect movemem,0,0,0,6,0

movemem: pshs y,u
 tfr d,x
 ldy 6,s
 ldu 8,s
 cmpx 6,s is the destination > source?
 bhi movehigh

movelow cmpu #2
 blo movelst1
 ldd ,y++
 std ,x++
 leau -2,u
 bra movelow
movelst1 cmpu #1
 bne moverts
 lda ,y
 sta ,x
moverts puls y,u,pc

movehigh tfr u,d
 leay d,y
 leax d,x

mloop1 cmpu #2
 blo movelst2
 ldd ,--y
 std ,--x
 leau -2,u
 bra mloop1
movelst2 cmpu #1
 bne moverts
 lda ,-y
 sta ,-x
 puls y,u,pc

 endsect


* C3_RMA_END
 ELSE
* Adapted from cmoc_os9/cgfx/todo/movemem.a for the live cmoc_os9 ABI.

        section code

_movemem                EXPORT * export this symbol

_movemem
        pshs    y,u
        ldx     6,s * load X from stack-relative value 6,s
        ldy     8,s * load Y from stack-relative value 8,s
        ldu     10,s * load U from stack-relative value 10,s
        cmpx    8,s * compare the destination pointer against the source pointer
        bhi     movehigh * copy backward when the regions overlap with destination above source

movelow cmpu    #2 * see whether at least two bytes remain to copy forward
        blo     movelst1 * fall through to the one-byte tail when fewer than two bytes remain
        ldd     ,y++ * load D from memory pointed to by Y+, then advance Y+
        std     ,x++ * store D to memory pointed to by X+, then advance X+
        leau    -2,u * subtract the copied word from the remaining byte count
        bra     movelow * continue the forward word-copy loop
movelst1
        cmpu    #1 * test whether a single trailing byte still needs copying
        bne     moverts * return immediately when the copy is complete
        lda     ,y * load A from memory pointed to by Y
        sta     ,x * store A to memory pointed to by X
moverts
        puls    y,u,pc * restore preserved registers and return

movehigh
        tfr     u,d * copy the byte count into D to form end pointers
        leay    d,y * advance Y to one byte past the source region
        leax    d,x * advance X to one byte past the destination region

mloop1  cmpu    #2 * see whether at least two bytes remain to copy backward
        blo     movelst2 * finish with the one-byte tail when only one byte remains
        ldd     ,--y * load D from memory pointed to by --Y
        std     ,--x * store D to memory pointed to by --X
        leau    -2,u * subtract the copied word from the remaining byte count
        bra     mloop1 * continue the backward word-copy loop
movelst2
        cmpu    #1 * test whether a final byte still needs copying
        bne     moverts * return immediately when the backward copy is complete
        lda     ,-y * load A from memory pointed to by -Y
        sta     ,-x * store A to memory pointed to by -X
        puls    y,u,pc * restore preserved registers and return

        endsect * end current section

 ENDC
