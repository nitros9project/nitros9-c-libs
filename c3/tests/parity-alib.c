#include <stdio.h>
int alibtest();
#asm
alibtest:
 pshs y,u
 ldd #12
 ldx #34
 lbsr MULT16
 cmpy #0
 bne afail
 cmpu #408
 bne afail
 ldd #7
 ldx #100
 lbsr DIV16
 cmpx #14
 bne afail
 cmpd #2
 bne afail
 ldb #$af
 lbsr BIN2HEX
 cmpd #$4146
 bne afail
 ldb #'z
 lbsr TO_UPPER
 cmpb #'Z
 bne afail
 clra
 clrb
 puls y,u,pc
afail
 ldd #1
 puls y,u,pc
#endasm
int main(void)
{
 if(alibtest()) { fputs("ALIB FAIL\r",stdout); return 1; }
 fputs("ALIB PASS\r",stdout);
 return 0;
}
