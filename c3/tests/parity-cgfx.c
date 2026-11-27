#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <cgfx.h>
#include <cgfx/mouse.h>
#include <cgfx/wind.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
static char expected[] = {
 27,41,2,3,0x12,0x34,
 27,42,4,5,
 27,43,6,7,8,0,9,0,10,0,11,
 27,44,12,13,0,14,0,15,0,16,0,17,
 27,45,18,19,0,20,0,21,
 27,32,1,2,3,4,5,6,7,8,
 27,64,0,22,0,23,
 27,50,24
};
int main(void)
{
    int path,n;
    char buffer[128],overlap[16];
    CHECK(sizeof(MSRET)==32);
    CHECK(sizeof(MIDSCR)==21 && sizeof(MNDSCR)==23 && sizeof(WNDSCR)==34);
    strcpy(overlap,"abcdef"); movemem(overlap+1,overlap,6);
    CHECK(memcmp(overlap,"aabcdef",7)==0);
    path=creat("gfx.tmp",3); CHECK(path>=0);
    CHECK(_cgfx_dfngpbuf(path,2,3,0x1234)==0);
    CHECK(_cgfx_kilbuf(path,4,5)==0);
    CHECK(_cgfx_gpload(path,6,7,8,9,10,11)==0);
    CHECK(_cgfx_getblk(path,12,13,14,15,16,17)==0);
    CHECK(_cgfx_putblk(path,18,19,20,21)==0);
    CHECK(_cgfx_dwset(path,1,2,3,4,5,6,7,8)==0);
    CHECK(_cgfx_setdptr(path,22,23)==0);
    CHECK(_cgfx_fcolor(path,24)==0);
    CHECK(Flush()==0); CHECK(close(path)==0);
    path=open("gfx.tmp",1); CHECK(path>=0);
    n=read(path,buffer,sizeof(buffer)); CHECK(close(path)==0);
    if (n!=sizeof(expected) || memcmp(buffer,expected,sizeof(expected))!=0) {
        printf("PACKET %d expected %d\r",n,sizeof(expected));
        for(path=0;path<n;++path) printf("%x ",buffer[path]);
        return 1;
    }
    fputs("CGFX PASS\r",stdout);
    return 0;
}
