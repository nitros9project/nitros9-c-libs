/* Environment-file API, originally by Mike Sweet (updated 8/6/90).
 * The C3 API takes a name and a value for putenv().
 * Bounds, missing names, and file truncation corrected during the shared port.
 */
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>

char *_ENVFILE = 0;
static char envstr[81];
static const char *filePath = "/dd/sys/env.file";

static char *readenv(void)
{
    int path, len;
    if (_ENVFILE) return _ENVFILE;
    _ENVFILE = malloc(1024);
    if (!_ENVFILE) return 0;
    path = open(filePath, 1);
    if (path < 0) { free(_ENVFILE); _ENVFILE=0; return 0; }
    len = read(path, _ENVFILE, 1023);
    close(path);
    if (len < 0) { free(_ENVFILE); _ENVFILE=0; return 0; }
    _ENVFILE[len]=0;
    return _ENVFILE;
}

static char *findenv(const char *name)
{
    char *line, *end, *value;
    int len, nlen;
    line=readenv();
    nlen=strlen(name);
    while (line && *line) {
        end=strchr(line,13);
        if (!end) end=line+strlen(line);
        value=line;
        while (value<end && *value!='=' && *value!=' ') ++value;
        len=value-line;
        if (*line!='*' && len==nlen && strnucmp(line,name,len)==0) {
            while (value<end && *value!='=') ++value;
            if (value<end) {
                ++value;
                while (value<end && *value==' ') ++value;
                return value;
            }
        }
        line=*end ? end+1 : end;
    }
    return 0;
}

char *getenv(const char *name)
{
    char *value, *end;
    int len;
    if (!name) return 0;
    value=findenv(name);
    if (!value) return 0;
    end=strchr(value,13);
    len=end ? end-value : strlen(value);
    if (len>80) len=80;
    memcpy(envstr,value,len); envstr[len]=0;
    return envstr;
}

int putenv(const char *name, const char *value)
{
    char *old, *end;
    int len, oldlen, size, path, result;
    if (!name || !*name || !value || strchr(name,'=') || strchr(name,13) || strchr(value,13)) return -1;
    old=findenv(name);
    if (!_ENVFILE) return -1;
    size=strlen(_ENVFILE); len=strlen(value);
    if (old) {
        end=strchr(old,13);
        if (!end) end=old+strlen(old);
        oldlen=end-old;
        if (size-oldlen+len>1023) return -1;
        movemem(old+len,end,strlen(end)+1);
        memcpy(old,value,len);
    } else {
        oldlen=strlen(name);
        if (size && _ENVFILE[size-1]!=13) {
            if (size==1023) return -1;
            _ENVFILE[size++]=13; _ENVFILE[size]=0;
        }
        if (size+oldlen+len+2>1023) return -1;
        strcat(_ENVFILE,name); strcat(_ENVFILE,"=");
        strcat(_ENVFILE,value); strcat(_ENVFILE,"\r");
    }
    path=creat(filePath,3);
    if (path<0) return -1;
    size=strlen(_ENVFILE);
    result=write(path,_ENVFILE,size);
    if (close(path)<0 || result!=size) return -1;
    return 0;
}
