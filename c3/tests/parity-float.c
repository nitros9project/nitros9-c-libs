#include <stdio.h>
#include <string.h>
#include <unistd.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d [%s]\r",__LINE__,out); return 1; }
int main(void)
{
    char out[384];

    sprintf(out,"%.2f",12.5); CHECK(strcmp(out,"12.50")==0);
    sprintf(out,"%.1f",1.25); CHECK(strcmp(out,"1.3")==0);
    sprintf(out,"%.3e",0.125); CHECK(strcmp(out,"1.250e-01")==0);
    sprintf(out,"%.4g",123.5); CHECK(strcmp(out,"123.5")==0);
    sprintf(out,"%f:%d",1.5,7); CHECK(strcmp(out,"1.500000:7")==0);
    sprintf(out,"%f",0.0); CHECK(strcmp(out,"0.000000")==0);
    fputs("FLOAT PASS\r",stdout);
    return 0;
}
