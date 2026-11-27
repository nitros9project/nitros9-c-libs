 IFDEF NITROS9_C3
* C3_RMA_BEGIN
***********************************
*
* Unbuffered write and flush
* code in the absense of buffering.
*
* by Mike Sweet 5/10/90
*
************************************
* Updated for the new C ABI on     *
* 12/27/2005 by tim lindner        *
************************************

 ifp1
* use /dd/defs/os9defs.a
 endc

 psect nobuffer,0,0,0,10,0

_cgfx_write:
 pshs y save y
 tfr u,y byte count to y
 os9 I$Write write it
 bcs error
 puls y
Flush:
_Flush:
 clra
 clrb
 rts

error puls y
 clra
 std errno,y
 ldd #-1
 rts return -1 on error


 endsect

* C3_RMA_END
 ELSE
***********************************
*
* Unbuffered write and flush
* code in the absense of buffering.
*
* by Mike Sweet 5/10/90
*

 section code

_errno EXTERN * import external symbol

_cgfx_write EXPORT * export this symbol
_cgfx_write:
 pshs y * preserve Y across the direct OS-9 write
 tfr u,y * move the requested byte count into Y for OS-9
 os9 $8A I$WRITE * write the caller's buffer directly without any intermediate buffering
 bcs error * branch to the errno path when OS-9 reports a write failure
 puls y * restore Y before returning success
_Flush:
 clra * clear A
 clrb * clear B
 rts * return to caller

error puls y * restore Y from the hardware stack
 clra * clear A
 std _errno,y * store D to indexed value _errno,y
 ldd #-1 * load D from immediate value -1
 rts * return -1 on error

 endsect * end current section

 ENDC
