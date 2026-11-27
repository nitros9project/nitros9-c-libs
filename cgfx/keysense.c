#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
******************************
* Keysense functions for
* MW C.  Include file is
* called "keysense.h"
* by Mike Sweet 8/31/89
*


 psect keysense,0,0,0,0,0
* use /dd/defs/os9defs.a


***********************************
* int _ss_ksns(path,keybits)
* int path,keybits;
*
* Set key sensing according to
* 'keybits' for the path 'path'
*


_ss_ksns:
 ldx 2,s get 'keybits'
 tfr b,a get native path
 ldb #$27 SS.KYSNS call
 os9 I$SETSTT
 bcs os9err error, return -1 and leave error code in 'errno'
 clra
 clrb
 rts else return 0 (success)

os9err
 clra
 std errno,y store the error number in 'errno'
 ldd #-1
 rts return -1 (error/failure)

**********************************
* _gs_ksns(path)
* int path;
*
* Returns key sense info from
* 'path' or -1 on error.
*


_gs_ksns:
 tfr b,a get native path
 ldb #$27 SS.KYSNS call
 os9 I$GETSTT
 bcs os9err
 tfr a,b
 clra
 rts return key status in D

* Modern interface stores the returned key flags through its second argument.
_os_gs_keysense:
 tfr b,a
 ldb #$27
 os9 I$GETSTT
 bcs os9err
 tfr a,b
 clra
 std [2,s]
 clrb
 rts

 endsect


* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm int
_os_ss_keysense(path_id path, int keys)
{
    asm
    {
_os9err EXTERNAL
_sysret EXTERNAL
		ldx 	2+2,s		get flags
		lda 	2+1,s		get byte
		ldb 	#SS_KySns
		os9 	I$SetStt
		lbra 	_sysret
	}
}
 
asm int
_os_gs_keysense(path_id path, int *keys)
{
    asm
    {
_os9err EXTERNAL
		lda 	2+1,s 		get the path
		ldb 	#SS_KySns
		os9 	I$GetStt
		lbcs 	_os9err
		tfr 	a,b
		clra
		std 	[4,s]		save the flags
		lbra 	_sysret
	}
}

#endif
