#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <setjmp.h>
#include <sets.h>
#include <time.h>
#include <unistd.h>
#include <fcntl.h>

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

    CHECK(strlen("abc") == 3);
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
    CHECK(_gs_rdy(255) == -1);
    for (i=0;i<256;i++) bytes[i] = i;
    file=fopen("nativebytes","w+"); CHECK(file != 0);
    CHECK(fwrite(bytes,1,256,file) == 256);
    CHECK(ftell(file) == 256L);
    CHECK(fseek(file,0L,SEEK_SET) == 0L);
    CHECK(fread(copy,1,256,file) == 256);
    CHECK(memcmp((const char *) bytes,(const char *) copy,256) == 0);
    CHECK(fclose(file) == 0);
    unlink("nativebytes");
    calendar.tm_year=100; calendar.tm_mon=0; calendar.tm_mday=1;
    calendar.tm_hour=calendar.tm_min=calendar.tm_sec=0;
    u2otime(&packet,&calendar);
    value=o2utime(&packet); CHECK(value == 946684800L);
    fputs("OS9TEXT PASS\r",stdout);
    write(2,"OS9TEXT STDERR\r",15);
    return 0;
}
