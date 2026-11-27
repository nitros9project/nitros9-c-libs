#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <os9.h>
#include <dbg.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
int main(void)
{
    registers_6809 regs;
    char packet[6];
    void *module;
    CHECK(strcmp(skipbl(" \tword"),"word")==0);
    CHECK(strcmp(skipwd("word next")," next")==0);
    CHECK(getime(packet)==0);
    memset(&regs,0,sizeof(regs));
    CHECK(_os9(F_ID,&regs)==0 && regs.a!=0);
    module=modlink("Init",0,0); CHECK(module!=(void *)-1 && module!=NULL);
    CHECK(munlink(module)==0);
    CHECK(modlink("no-such-module",0,0)==(void *)-1);
    CHECK(freemem()>0);
    fputs("SYSTEM PASS\r",stdout); return 0;
}
