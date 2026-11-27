/* Binary64 front end for the preserved assembly decimal digit extractor.
 * The scaling/digit algorithm follows the historical C3 pffinit.c formatter.
 */
#include <stdlib.h>
#include <string.h>

int _abnorm(double *value);
int _outdig(double *value);

char *ftoa(char *out, double value)
{
    char *bytes, *p;
    int exponent, power, negative, decimal, digit, i;
    bytes=(char *)&value;
    negative=bytes[0]&0x80;
    exponent=((bytes[0]&0x7f)<<4)|((bytes[1]&0xff)>>4);
    p=out;
    if (negative) *p++='-';
    if (exponent==2047) {
        for (i=1;i<8;i++)
            if ((bytes[i]&0xff) != (i==1 ? 0xf0 : 0)) {
                strcpy(out,"nan"); return out;
            }
        strcpy(p,"inf"); return out;
    }
    if ((bytes[0]&0x7f)==0 && (bytes[1]|bytes[2]|bytes[3]|bytes[4]|bytes[5]|bytes[6]|bytes[7])==0) {
        strcpy(p,"0"); return out;
    }
    bytes[0]&=0x7f;
    exponent-=1023;
    power=(exponent*78)>>8;
    decimal=power;
    value=scale(value,power<0 ? -power : power,power<0);
    while (value<1.0) { value*=10.0; decimal--; }
    while (value>=10.0) { value/=10.0; decimal++; }
    _abnorm(&value);
    for (i=0;i<18;i++) {
        digit=_outdig(&value);
        *p++=digit;
        if (i==0) *p++='.';
    }
    *p++='E';
    *p++=decimal<0 ? '-' : '+';
    if (decimal<0) decimal=-decimal;
    *p++=decimal/100+'0';
    *p++=(decimal/10)%10+'0';
    *p++=decimal%10+'0';
    *p=0;
    return out;
}
