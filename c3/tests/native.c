#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <setjmp.h>
#include <sets.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>
#include <dir.h>
#include <signal.h>

#define CHECK(test) if (!(test)) { printf("FAIL %d\n", __LINE__); return 1; }
static int compare(const void *a, const void *b)
{
    return *(const int *) a - *(const int *) b;
}

int main(void)
{
    char buffer[64], *end, *set;
    unsigned char bytes[256], copy[256];
    int values[5], key = 3, i;
    FILE *file;
    jmp_buf context;
    long value;
    union { unsigned long value; unsigned words[2]; } number;
    struct tm calendar;
    _os_time packet;
    DIR directory;
    long now;

    CHECK(strlen("abc") == 3);
    CHECK(memset(buffer,'X',3) == buffer && buffer[0] == 'X' && buffer[2] == 'X');
    CHECK(memset(buffer,'Y',0) == buffer && buffer[0] == 'X');
    CHECK(strcmp(strcpy(buffer,"ab"),"ab") == 0);
    CHECK(strcmp(strcat(buffer,"cd"),"abcd") == 0);
    CHECK(strchr(buffer,0) == buffer+4);
    CHECK(strrchr(buffer,0) == buffer+4);
    CHECK(strspn("abcde","abc") == 3);
    CHECK(strcspn("abcde","de") == 3);
    CHECK(strpbrk(buffer,"bd") == buffer+1);
    CHECK(strucmp("AbCd","aBcD") == 0);
    CHECK(strnucmp("abC!","ABc?",3) == 0);
    CHECK(strcmp(strucpy(buffer,"ab7"),"AB7") == 0);
    CHECK(strcmp(strucat(buffer,"cd"),"AB7CD") == 0);
    CHECK(tolower(0) == 0 && toupper('7') == '7');
    CHECK(tolower('A') == 'a' && toupper('z') == 'Z');
    CHECK(strcmp(itoa(-32767-1,buffer),"-32768") == 0);
    CHECK(strcmp(utoa(65535U,buffer),"65535") == 0);
    CHECK(strcmp(ltoa(-2147483647L-1L,buffer),"-2147483648") == 0);
    CHECK(strcmp(ltoa(0L,buffer),"0") == 0);
    CHECK(strcmp(ltoa(2147483647L,buffer),"2147483647") == 0);
    CHECK(strcmp(ltoa(-123L,buffer),"-123") == 0);
    CHECK(atol("123456789") == 123456789L);
    CHECK(htol("12345678") == 0x12345678L);
    CHECK(strtol("-2147483648!",&end,10) == (-2147483647L-1L) && *end == '!');
    CHECK(strtol("2147483648",0,10) == 2147483647L);
    number.value = strtoul("4294967295",0,10);
    CHECK(number.words[0] == 65535U && number.words[1] == 65535U);
    number.value = strtoul("4294967296",0,10);
    CHECK(number.words[0] == 65535U && number.words[1] == 65535U);
    for (i=0;i<5;i++) values[i] = 5-i;
    qsort(values,5,sizeof(int),compare);
    CHECK(values[0] == 1 && values[4] == 5);
    CHECK(bsearch(&key,values,5,sizeof(int),compare) == &values[2]);
    for (key=1;key<=5;key++)
        CHECK(bsearch(&key,values,5,sizeof(int),compare) == &values[key-1]);
    key=0; CHECK(bsearch(&key,values,5,sizeof(int),compare) == 0);
    key=6; CHECK(bsearch(&key,values,5,sizeof(int),compare) == 0);
    key=1; CHECK(bsearch(&key,values,0,sizeof(int),compare) == 0);
    CHECK(bsearch(&key,values,1,sizeof(int),compare) == values);
    key=2; CHECK(bsearch(&key,values,1,sizeof(int),compare) == 0);
    i=setjmp(context);
    if (!i) longjmp(context,7);
    CHECK(i == 7);
    set=allocset(); CHECK(set != 0);
    addc2set(set,'A'); CHECK(smember(set,'A') && !smember(set,'B'));
    rmfmset(set,'A'); CHECK(!smember(set,'A'));
    free(set);
    i=sprintf(buffer,"%05d %s %ld",12,"abc",123456L);
    CHECK(i == 16);
    CHECK(strcmp(buffer,"00012 abc 123456") == 0);
    CHECK(sprintf(buffer,"%f:%d",1.0,7) == 2);
    CHECK(strcmp(buffer,":7") == 0);
    signal(SIGINT,SIG_IGN);
    CHECK(signal(SIGINT,SIG_DFL) == SIG_IGN);
    CHECK(_gs_rdy(255) == -1);
    CHECK(getstat(1,255,0,0) == -1);
    CHECK(_os_getstat(1,255,0,0) != 0);
    CHECK(setstat(0,255,0,0,0) == -1);
    CHECK(_os_setstat(0,255,0,0,0) != 0);
    for (i=0;i<256;i++) bytes[i] = i;
    file=fopen("nativebytes","w+"); CHECK(file != 0);
    CHECK(fwrite(bytes,1,256,file) == 256);
    CHECK(ftell(file) == 256L);
    CHECK(fseek(file,0L,SEEK_SET) == 0L);
    CHECK(fread(copy,1,256,file) == 256);
    CHECK(memcmp((const char *) bytes,(const char *) copy,256) == 0);
    CHECK(fclose(file) == 0);
    file=fdopen(open("nativebytes",1),"r"); CHECK(file != 0);
    CHECK(getc(file) == 0);
    CHECK(freopen("nativebytes","r",file) == file);
    CHECK(getc(file) == 0);
    CHECK(fseek(file,20L,SEEK_SET) == 0L);
    CHECK(getc(file) == 20);
    CHECK(fseek(file,-2L,SEEK_CUR) == 0L);
    CHECK(getc(file) == 19);
    CHECK(fseek(file,-1L,SEEK_END) == 0L);
    CHECK(getc(file) == 255);
    rewind(file); CHECK(getc(file) == 0);
    CHECK(fclose(file) == 0);
    file=fopen("nativebytes","a"); CHECK(file != 0);
    CHECK(fseek(file,0L,SEEK_SET) == 0L);
    CHECK(putc('Z',file) == 'Z');
    CHECK(fclose(file) == 0);
    directory.dd_fd=open("nativebytes",1);
    CHECK(directory.dd_fd >= 0);
    CHECK(telldir(&directory) == 0L);
    seekdir(&directory,255L);
    CHECK(telldir(&directory) == 255L);
    CHECK(lseek(directory.dd_fd,0L,SEEK_END) == 257L);
    CHECK(lseek(directory.dd_fd,-1L,SEEK_END) == 256L);
    CHECK(read(directory.dd_fd,buffer,1) == 1 && buffer[0] == 'Z');
    seekdir(&directory,0L);
    CHECK(telldir(&directory) == 0L);
    CHECK(close(directory.dd_fd) == 0);
    unlink("nativebytes");
    i=creat("nativecreate",2); CHECK(i >= 0);
    CHECK(write(i,"X",1) == 1); CHECK(close(i) == 0);
    i=ocreat("nativecreate",2,PMODE); CHECK(i >= 0);
    CHECK(lseek(i,0L,SEEK_END) == 0L); CHECK(close(i) == 0);
    unlink("nativecreate");
    calendar.tm_year=100; calendar.tm_mon=0; calendar.tm_mday=1;
    calendar.tm_hour=calendar.tm_min=calendar.tm_sec=0;
    u2otime(&packet,&calendar);
    CHECK(packet.month == 1);
    value=o2utime(&packet); CHECK(value == 946684800L);
    value=time(&now); CHECK(value != -1L && value == now);
    CHECK(time(0) != -1L);
    fputs("OS9TEXT PASS\r",stdout);
    write(2,"OS9TEXT STDERR\r",15);
    return 0;
}
