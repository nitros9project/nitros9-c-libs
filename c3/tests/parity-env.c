#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
extern char *_ENVFILE;
int main(void)
{
 FILE *file;
 char text[128],*value;
 file=fopen("/dd/sys/env.file","w"); CHECK(file!=NULL);
 fputs("* comment\rNAME=long value\rNAM=separate\r",file); CHECK(fclose(file)==0);
 CHECK(getenv("missing")==NULL);
 CHECK(strcmp(getenv("name"),"long value")==0);
 CHECK(strcmp(getenv("NAM"),"separate")==0);
 CHECK(putenv("NAME","x")==0);
 CHECK(strcmp(getenv("name"),"x")==0);
 CHECK(putenv("ADDED","new")==0);
 CHECK(strcmp(getenv("ADDED"),"new")==0);
 free(_ENVFILE); _ENVFILE=0;
 CHECK(strcmp(getenv("name"),"x")==0);
 CHECK(strcmp(getenv("ADDED"),"new")==0);
 CHECK(putenv("BAD=NAME","bad")==-1);
 fputs("ENV PASS\r",stdout); return 0;
}
