#ifdef NITROS9_C3
#asm
* C3_RMA_BEGIN
**********************************
* Primitive sound function
* provided through CoCo 3
* SS.Tone SetStat call
*
* by Mike Sweet 9/1/89
*

 psect sound,0,0,0,0,0

* use /dd/defs/os9defs.a


************************************************
* _ss_tone(path,duration,volume,frequency)
* int path,duration,volume,frequency;
*
* Sound a tone through the speaker for
* 'duration' ticks at specified frequency
* (0-4095) and volume (0-63).  Frequency
* is not actual, but relative.(<> Hz)
*
*

_ss_tone:
 pshs y,b
 lbsr _Flush
 lda 8,s get volume
 ldb 6,s get duration
 tfr d,x
 ldy 9,s get frequency
 lda ,s get path
 ldb #$98 SS.Tone call
 os9 I$SETSTT
 clra
 clrb
 leas 1,s
 puls y,pc return 0

 endsect





* C3_RMA_END
#endasm
#else
#include <cgfx.h>

asm error_code
_cgfx_ss_tone(path_id path, int duration, int volume, int frequency)
{
    asm
    {
_Flush	EXTERNAL
_sysret	EXTERNAL
		pshs y
		lbsr _Flush
		lda 9,s get volume
		ldb 7,s get duration
		tfr d,x
		ldy 10,s get frequency
		lda 5,s get path
		ldb #$98 SS.Tone call
		os9 I$SetStt
		lbra	_sysret
	}
} 




#endif
