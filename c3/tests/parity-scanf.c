#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
static union { double value; unsigned word[4]; } number;
int main(void)
{
    int a,b,n;
    unsigned hex,octal;
    char text[32], input[64], letter;
    long value;
    FILE *file;
    number.value=atof("12.5");
    CHECK(number.word[0]==0x4029 && number.word[1]==0 && number.word[2]==0 && number.word[3]==0);
    number.value=atof("-0.5");
    CHECK(number.word[0]==0xbfe0 && number.word[1]==0 && number.word[2]==0 && number.word[3]==0);
    strcpy(input,"42 -7 word");
    n=sscanf(input,"%d %d %s",&a,&b,text);
    CHECK(n==3 && a==42 && b==-7 && strcmp(text,"word")==0);
    CHECK(sscanf("1234567","%ld",&value)==1 && value==1234567L);
    CHECK(sscanf("ff 17","%x %o",&hex,&octal)==2 && hex==255 && octal==15);
    CHECK(sscanf("12345","%3d%2d",&a,&b)==2 && a==123 && b==45);
    CHECK(sscanf("skip 19Q","%*s %d%c",&a,&letter)==2 && a==19 && letter=='Q');
    CHECK(sscanf("12.5","%lf",&number.value)==1);
    CHECK(number.word[0]==0x4029 && number.word[1]==0 && number.word[2]==0 && number.word[3]==0);
    file=fopen("scan.tmp","w"); CHECK(file!=NULL);
    CHECK(fputs("31 file",file)>=0); CHECK(fclose(file)==0);
    file=fopen("scan.tmp","r"); CHECK(file!=NULL);
    CHECK(fscanf(file,"%d %s",&a,text)==2 && a==31 && strcmp(text,"file")==0);
    CHECK(fclose(file)==0);
    CHECK(sscanf("0","%ld",&value)==1 && value==0L);
    CHECK(sscanf("","%ld",&value)==EOF);
    a=123;
    CHECK(sscanf("  ","%d",&a)<=0 && a==123);
    CHECK(sscanf("","%s",text)==EOF);
    fputs("SCAN PASS\r",stdout);
    return 0;
}
