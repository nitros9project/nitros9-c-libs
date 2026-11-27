 IFDEF NITROS9_C3
* C3_RMA_BEGIN
*********************************************
*
* Buffering routines for CGFX library.
* These are included by including a call to
* '_Flush()' in your program.
*
* Any output to a path is buffered until
* one of the following conditions is met:
*
*  - you write to a different path
*  - you call _ss_mgpb(), _ss_wset(), GetBlk(),
*    writeln(), cwriteln(), read(), readln(),
*    cread(), creadln(), GPLoad(), or KilBuf().
*  - you call the _Flush() function to flush
*    the buffer.
*
* Many thanks to Eddie Kuns, who suggested
* transparent buffering for this lib and
* kept me thinking about it.
* Also, thanks to Bob van der Poel for reminding
* me to return an error if _Flush() is unsuccessful....
*
* CGFX replacement lib buffering routines
* by Mike Sweet 5/10/90,8/11/90
************************************
* Updated for the new C ABI on     *
* 12/25/2005 by tim lindner        *
* (actually there was nothing to   *
* adjust)                          *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect cbuffer,0,0,0,10,0

 vsect
_CBuffer: rmb 256 this is the buffer for all output
_CUsed: fdb 0 this is 'how much is used' in the buffer
_CPath: fcb -1 the path all of this has to go to
 endsect

Flush:
_Flush:
 clra
 clrb
 pshs d,x,y,u save important registers

 tfr y,u
 lda _CPath,y
 bmi noerror1
 leax _CBuffer,y
 ldy _CUsed,y
 beq noerror1
 os9 I$Write
 bcc noerror1 thanks Bob!
 clra
 std errno,u
 ldd #-1
 std ,s

noerror1
 clra
 clrb
 std _CUsed,u
 puls d,x,y,u,pc


*********************************
* Previously (version 5), you
* had to call _CGFXBuf() to init
* the buffer data structure.  No
* longer, tho....
*

_CGFXBuf:
 rts


**************************************
* write function- used for all other
* functions to write to a path-
* unbuffered version just calls I$WRITE.
*
* A=path
* X=address
* U=byte count
*

_cgfx_write:
 cmpa _CPath,y writing to a different path?
 beq noflush1 no, don't flush yet...

* fix for version 7!
 pshs a save old path (_Flush will overwrite...)

 bsr _Flush ok, flush everything

*fix for version 7!
 puls a restore old path....
 sta _CPath,y set new path

noflush1 tfr u,d byte count to D
 addd _CUsed,y
 cmpd #256 buffer going to fill up?
 blo noflush2 nope
 bsr _Flush flush the buffer if so...

noflush2 cmpu #256 writing more than 256 bytes?
 blo bufferit nope, stick it in the buffer
 pshs y otherwise, write it directly
 lda _CPath,y get the path
 tfr u,y y=byte count
 os9 I$Write write it
 puls y
 bcc noerror2 no error...
 clra
 std errno,y save the error number
 ldd #-1 return -1
return rts

noerror2 clra
 clrb
 rts return 0


bufferit ldd _CUsed,y
 pshs u save byte count
 leau _CBuffer,y
 leau d,u get offset into buffer
 ldd ,s and byte count

bloop lda ,x+
 sta ,u+
 decb only sending <256 bytes...
 bne bloop loop till all bytes copied

 puls d get byte count
 addd _CUsed,y update used count
 std _CUsed,y

 clra
 clrb
 rts return 0

 endsect

* C3_RMA_END
 ELSE
*********************************************
*
* Buffering routines for CGFX library.
* These are included by including a call to
* '_CGFXBuf()' in your program.  This function
* just initializes the buffer used and returns.
*
* Any output to a path is buffered until
* one of the following conditions is met:
*
*  - you write to a different path
*  - you call _ss_mgpb(), _ss_wset(), GetBlk(),
*    writeln(), cwriteln(), read(), readln(),
*    cread(), creadln(), GPLoad(), or KilBuf().
*  - you call the _Flush() function to flush
*    the buffer.
*
* The _Flush() function call be called whether
* or not buffering is used.  If you have a set
* of functions that you regularly use that do
* screen output, the _Flush() call can be used
* safely (it is a NULL function without
* buffering.)
*
* Many thanks to Eddie Kuns, who suggested
* transparent buffering for this lib and
* kept me thinking about it.
* Also, thanks to Bob van der Poel for reminding
* me to return an error if _Flush() is unsuccessful....
*
* CGFX replacement lib buffering routines
* by Mike Sweet 5/10/90,8/11/90
*

 section bss
_CBuffer: rmb 256 this is the buffer for all output
_CUsed: fdb 0 this is 'how much is used' in the buffer
_CPath: fcb -1 the path all of this has to go to
 endsect * end current section

 section code
_errno EXTERNAL * import external symbol
_Flush EXPORT * export this symbol
_Flush:
 clra * clear A
 clrb * clear B
 pshs d,x,y,u * save caller-visible registers before touching OS-9 state

 tfr y,u * keep the static data pointer in U for the rest of the routine
 lda _CPath,y * load A from indexed value _CPath,y
 bmi noerror1 * skip the write when no buffered path is active
 leax _CBuffer,y * compute effective address into X from _CBuffer,y
 ldy _CUsed,y * load Y from indexed value _CUsed,y
 beq noerror1 * skip the write when the buffer is already empty
 os9 $8A I$Write * write the buffered bytes to the active path
 bcc noerror1 * leave errno alone when the flush succeeds
 clra * clear A
 std _errno,u * store D to indexed value _errno,u
 ldd #-1 * load D from immediate value -1
 std ,s * overwrite saved D so the caller receives -1 on failure

noerror1
 clra * clear A
 clrb * clear B
 std _CUsed,u * store D to indexed value _CUsed,u
 puls d,x,y,u,pc


*********************************
* Previously (version 5), you
* had to call _CGFXBuf() to init
* the buffer data structure.  No
* longer, tho....
*

_CGFXBuf:
 rts * return to caller


**************************************
* write function- used for all other
* functions to write to a path-
* unbuffered version just calls I$WRITE.
*
* A=path
* X=address
* U=byte count
*

_cgfx_write EXPORT * export this symbol
_cgfx_write:
 cmpa _CPath,y * check whether the new write uses the current buffered path
 beq noflush1 * keep buffering when the path has not changed

* fix for version 7! 
 pshs a * preserve the requested path because _Flush clobbers A

 bsr _Flush * flush buffered output before switching paths

*fix for version 7!
 puls a * recover the requested destination path
 sta _CPath,y * record the destination path for subsequent buffered writes

noflush1 tfr u,d * copy the requested byte count into D
 addd _CUsed,y * add indexed value _CUsed,y into D
 cmpd #256 * see whether appending this write would overflow the buffer
 blo noflush2 * keep buffering when the combined size still fits
 bsr _Flush * flush existing buffered data before appending more

noflush2 cmpu #256 * test whether the caller wants to write a full buffer or more
 blo bufferit * copy smaller writes into the buffer instead of writing now
 pshs y * preserve Y because OS-9 expects the byte count there
 lda _CPath,y * fetch the active destination path
 tfr u,y * move the byte count into Y for OS-9
 os9 $8A I$Write * send large writes directly to the path without buffering
 puls y
 bcc noerror2 * return success when the direct write worked
 clra * clear A
 std _errno,y * store the OS-9 error code in errno
 ldd #-1 * return -1 to report the direct-write failure
return rts * return to caller

noerror2 clra * clear A
 clrb * clear B
 rts * return 0 for a successful direct write


bufferit ldd _CUsed,y * load D from indexed value _CUsed,y
 pshs u * preserve the requested byte count while U is reused as a pointer
 leau _CBuffer,y * compute effective address into U from _CBuffer,y
 leau d,u * advance U to the first free byte in the buffer
 ldd ,s * recover the requested byte count into D

bloop lda ,x+ * load A from memory pointed to by X, then advance X
 sta ,u+ * store A to memory pointed to by U, then advance U
 decb * count one buffered byte copied
 bne bloop * keep copying until the caller's byte count reaches zero

 puls d * restore the original byte count
 addd _CUsed,y * add the copied byte count to the buffered-usage total
 std _CUsed,y * store D to indexed value _CUsed,y

 clra * clear A
 clrb * clear B
 rts * return 0 after buffering the write successfully

 endsect * end current section

 ENDC
