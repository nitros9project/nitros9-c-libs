#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <dbg.h>
#define CHECK(x) if (!(x)) { printf("FAIL %d\r",__LINE__); return 1; }
int main(void)
{
 int saved,path,n,count,i;
 char buffer[128],*first;
 saved=dup(2); CHECK(saved>=0);
 CHECK(close(2)==0);
 path=creat("trace.tmp",3); CHECK(path==2);
 _trace(TRON); _prof(0,"probe"); _eprof("probe"); _trace(TROFF);
 CHECK(close(2)==0); CHECK(dup(saved)==2); CHECK(close(saved)==0);
 path=open("trace.tmp",1); CHECK(path>=0);
 n=read(path,buffer,127); CHECK(n>0); buffer[n]=0; CHECK(close(path)==0);
 count=0;
 for(i=0;i+5<=n;i++) if(strncmp(buffer+i,"probe",5)==0) ++count;
 CHECK(count==2);
 fputs("DEBUG PASS\r",stdout); return 0;
}
