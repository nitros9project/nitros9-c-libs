 IFDEF NITROS9_C3
* C3_RMA_BEGIN
******************************************
* C read and write functions
* by Mike Sweet 1/4/90
******************************************
* Updated to new ABI by tim lindner      *
* December 26, 2005                      *
******************************************
*

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect crw,0,0,0,20,0


****************************************************
*
* cread(path,s,n);
* int path,n;
* char *s;
*
* Reads up to 'n' characters.  Replaces the CR with a NULL.
*

cread:pshs b,y
 lbsr _Flush
 puls a
 ldy 6,s
 ldx 4,s
 os9 I$ReadLn
 bcs os9err
 leay -1,y
 ldx 4,s
 tfr y,d
 leax d,x
 lda ,x
 cmpa #13
 beq c2
 leax 1,x
c2 clr ,x
 tfr y,d
 puls y,pc



****************************************************
*
* creadln(path,s,n);
* int path,n;
* char *s;
*
* Reads up to 'n' characters.  Appends a NULL to
* the end of the string.
*

creadln: pshs b,y
 lbsr _Flush
 puls a
 ldy 6,s
 ldx 4,s
 os9 I$ReadLn
 bcs os9err
 ldx 4,s
 tfr y,d
 clr d,x
 puls y,pc


os9err
 puls y
 clra
 std errno,y
 ldd #-1
 rts

************************************************
*
* cwrite(path,s,n);
* int path,n;
* char *s;
*
* 'cwrite()' will write up to 'n'charatcers to path
* using the I$WRITE call.  If 's' is shorter than 'n'
* characters then only 's' characters are written.
*

cwrite:
 pshs u,b
 ldx 5,s *s
 tfr x,d
 lbsr strlen
 cmpd 7,s n
 blo c0
 ldd 7,s n
c0 tfr d,u
 puls a
 pshs u
 ldx 6,s *s
 lbsr _cgfx_write
 bcs os9err2
 puls d,u,pc


os9err2 clra
 std errno,y
 leas 2,s
 ldd #-1
 puls u,pc


************************************************
*
* cwriteln(path,s,n);
* int path,n;
* char *s;
*
* 'cwriteln()' will write up to 'n'charatcers to path
* using the I$WRITELN call.  If 's' is shorter than 'n'
* characters then only 's' characters are written.
*

cwriteln:
 pshs b,y
 lbsr _Flush
 ldx 5,s *s
 tfr x,d
 lbsr strlen
 cmpd 7,s n
 blo c1
 ldd 7,s n
c1 tfr d,y
 ldx 5,s *s
 puls a path
 os9 I$WritLn
 bcs os9err
 tfr y,d
 puls y,pc



****************************************************
*
* read(path,s,n);
* int path,n;
* char *s;
*
* Reads up to 'n' characters.
*

read:
 pshs b,y
 lbsr _Flush
 puls a path
 ldy 6,s n
 ldx 4,s *s
 os9 I$Read
 bcs os9err
 tfr y,d
 puls y,pc



****************************************************
*
* readln(path,s,n);
* int path,n;
* char *s;
*
* Reads up to 'n' characters.
*

readln:
 pshs b,y
 lbsr _Flush
 puls a path
 ldy 6,s n
 ldx 4,s *s
 os9 I$ReadLn
 lbcs os9err
 tfr y,d
 puls y,pc


************************************************
*
* write(path,s,n);
* int path,n;
* char *s;
*
* 'write()' will write up to 'n' characters to path
* using the I$WRITE call.
*

write:
 pshs u
 ldx 4,s *s
 ldu 6,s n
 tfr b,a path
 lbsr _cgfx_write
 lbcs os9err2
 puls u,pc


************************************************
*
* writeln(path,s,n);
* int path,n;
* char *s;
*
* 'writeln()' will write up to 'n' characters to path
* using the I$WRITELN call.
*

writeln:
 pshs b,y
 lbsr _Flush
 ldx 5,s *s
 ldy 7,s n
 puls a path
 os9 I$WritLn
 lbcs os9err
 tfr y,d
 puls y,pc


 endsect

* C3_RMA_END
 ELSE
* Adapted from cmoc_os9/cgfx/todo/crw.a for the live cmoc_os9 ABI.

        section code

_cread                  EXPORT * export this symbol
_creadln                EXPORT * export this symbol
_cwrite                 EXPORT * export this symbol
_cwriteln               EXPORT * export this symbol

_errno                  EXTERNAL * import external symbol
_Flush                  EXTERNAL * import external symbol
_strlen                 EXTERNAL * import external symbol
_cgfx_write             EXTERNAL * import external symbol

_cread
        lbsr    _Flush * flush any pending buffered output before blocking for input
        pshs    y
        lda     5,s * load the input path number
        ldy     8,s * load the maximum byte count for the read
        ldx     6,s * load the caller's destination buffer
        os9     $8B * perform an OS-9 read into the caller's buffer
        bcs     os9err * branch to the shared errno path if OS-9 reports an error
        leay    -1,y * convert the returned byte count to the index of the last byte read
        ldx     6,s * reload the caller's destination buffer
        tfr     y,d * copy the final-byte index into D for address arithmetic
        leax    d,x * point X at the last byte that OS-9 stored
        lda     ,x * load the last character that was read
        cmpa    #13 * test whether the last character is a carriage return
        beq     cread_null * branch if equal/zero to cread_null
        leax    1,x * advance past the last character when no CR stripping is needed
cread_null
        clr     ,x * append a NUL terminator after the returned text
        tfr     y,d * return the character count in D
        puls    y,pc

_creadln
        lbsr    _Flush * flush any pending buffered output before blocking for input
        pshs    y
        lda     5,s * load the input path number
        ldy     8,s * load the maximum byte count for the read
        ldx     6,s * load the caller's destination buffer
        os9     $8B * perform an OS-9 read into the caller's buffer
        bcs     os9err * branch to the shared errno path if OS-9 reports an error
        ldx     6,s * reload the caller's destination buffer
        tfr     y,d * copy the returned byte count into D
        clr     d,x * append a NUL terminator after the received line
        puls    y,pc

os9err
        puls    y
        clra * clear A
        std     _errno,y * preserve the OS-9 error code in errno
        ldd     #-1 * load D from immediate value -1
        rts * return to caller

_cwrite
        pshs    u
        ldx     6,s * load the caller's string pointer
        pshs    x
        lbsr    _strlen * measure the string length before writing it
        leas    2,s * discard the temporary _strlen argument
        cmpd    8,s * compare the string length against the caller's maximum count
        blo     cwrite_len_ok * keep the string length when it is already within the limit
        ldd     8,s * clamp the write length to the caller-supplied maximum
cwrite_len_ok
        tfr     d,u * move the chosen write length into U for _cgfx_write
        pshs    u
        ldx     8,s * reload the string pointer
        lda     7,s * load the output path number
        lbsr    _cgfx_write * send the bounded byte count through the buffered writer
        bcs     os9err2 * branch if the write helper returned an error
        puls    d,u,pc * discard the saved length and return the byte count in D

os9err2
        clra * clear A
        std     _errno,y * preserve the write error code in errno
        leas    2,s * discard the saved write length before returning
        ldd     #-1 * load D from immediate value -1
        puls    u,pc

_cwriteln
        lbsr    _Flush * flush any pending buffered output before issuing writeln
        pshs    y
        ldx     6,s * load the caller's string pointer
        pshs    x
        lbsr    _strlen * measure the string length before writing it with a newline
        leas    2,s * discard the temporary _strlen argument
        cmpd    8,s * compare the string length against the caller's maximum count
        blo     cwriteln_len_ok * keep the string length when it already fits
        ldd     8,s * clamp the output length to the caller-supplied maximum
cwriteln_len_ok
        tfr     d,y * move the bounded output length into Y for OS-9 writeln
        ldx     6,s * reload the string pointer
        lda     5,s * load the output path number
        os9     $8C * write the string followed by a carriage return/newline
        bcs     os9err * branch to the shared errno path if OS-9 reports an error
        tfr     y,d * return the number of characters written in D
        puls    y,pc

        endsect * end current section

 ENDC
