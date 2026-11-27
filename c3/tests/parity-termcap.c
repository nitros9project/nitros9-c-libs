#include <stdio.h>
#include <string.h>
#include <termcap.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
int main(void)
{
 char buffer[128],*value;
 value=tparam("row %d col %d",buffer,sizeof(buffer),12,34,0,0);
 CHECK(value==buffer && strcmp(buffer,"row 12 col 34")==0);
 value=tgoto("%i%d;%d",4,2);
 CHECK(strcmp(value,"3;5")==0);
 value=tparam("%r%d/%d",buffer,sizeof(buffer),1,2,0,0);
 CHECK(strcmp(value,"2/1")==0);
 CHECK(crtbynam("/no-such-device",buffer)==NULL);
 fputs("TERMCAP PASS\r",stdout); return 0;
}
