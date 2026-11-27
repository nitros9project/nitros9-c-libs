#ifndef _TERMCAP_H
#define _TERMCAP_H
/* Historical parameter expansion and OS-9 ttytype lookup API. */
char *tparam(const char *format, char *buffer, int length, int a, int b, int c, int d);
char *tgoto(const char *format, int column, int row);
char *crtbynam(const char *device, char *buffer);
char *crtbypth(int path, char *buffer);
extern char *BC, *UP;
#endif
