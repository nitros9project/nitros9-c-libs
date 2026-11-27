#include "cmoc_os9.h"
#include <errno.h>
#include <stddef.h>
#include <stdint.h>
#include <os9raw.h>

static int legacy(int code) { return code ? (errno = code, -1) : 0; }

int getstat(int c, int p, void *a, void *b) {
  return legacy(cmoc_os_getstat(c, p, a, b));
}
int setstat(int c, int p, void *a, void *b, void *d) {
  return legacy(cmoc_os_setstat(c, p, a, b, d));
}

int cmoc_legacy_getuid(void) {
  int v;
  return cmoc_os_getuid(&v) ? -1 : v;
}
int cmoc_legacy_getpid(void) {
  int v;
  return cmoc_os_getpid(&v) ? -1 : v;
}
int cmoc_setuid(int uid) { return legacy(cmoc_os_setuid(uid)); }

int cmoc_wait(int *s) { return cmoc_os_wait(s); }
int setpr(int p, int v) { return legacy(cmoc_os_setpr(p, v)); }
int cmoc_kill(int p, int s) { return legacy(cmoc_os_send(p, s)); }

int os9fork(const char *n, int l, void *a, int lang, int type, int pages) {
  int p;
  return cmoc_os_fork(n, l, a, lang, type, pages, &p) ? -1 : p;
}
int chain(const char *n, int l, void *a, int lang, int type, int pages) {
  return legacy(cmoc_os_chain(n, l, a, lang, type, pages));
}

clock_t tsleep(clock_t t) {
  int n = (uint16_t)t;
  return cmoc_os9_sleep(&n) ? (clock_t)-1 : (unsigned)n;
}
int cmoc_sleep(int seconds) {
  unsigned t = (unsigned)seconds * 60;
  clock_t left = tsleep(t);
  return left == (clock_t)-1 ? -1 : (int)((left + 59) / 60);
}
int cmoc_pause(void) {
  int t = 0;
  return legacy(cmoc_os9_sleep(&t));
}
int prerr(int p, int e) {
  return legacy(n9_prerr(p, e));
}
long _gs_size(int p) {
  long v;
  return cmoc_os_getstat(SS_Size, p, &v, 0) ? -1 : v;
}
long _gs_pos(int p) {
  long v;
  return cmoc_os_getstat(SS_Pos, p, &v, 0) ? -1 : v;
}
int _gs_rdy(int p) {
  int v;
  return cmoc_os_gs_ready(p, &v) ? -1 : v;
}
int _gs_eof(int p) {
  int v;
  return cmoc_os_gs_eof(p, &v) ? -1 : v;
}
int _gs_opt(int p, void *v) { return cmoc_os_getstat(SS_Opt, p, v, 0); }
int _gs_devn(int p, char *v) { return cmoc_os_getstat(SS_DevNm, p, v, 0); }
int _gs_gfd(int p, void *v, int n) {
  return cmoc_os_getstat(SS_FD, p, v, (void *)(uintptr_t)(unsigned)n);
}
int _ss_opt(int p, void *v) { return cmoc_os_setstat(SS_Opt, p, v, 0, 0); }
int _ss_pfd(int p, void *v) { return cmoc_os_setstat(SS_FD, p, v, 0, 0); }
int _ss_ssig(int p, void *v) { return cmoc_os_setstat(SS_SSig, p, v, 0, 0); }
int _ss_tiks(int p, void *v) { return cmoc_os_setstat(SS_Ticks, p, v, 0, 0); }
int _ss_rest(int p, void *v) { return cmoc_os_setstat(SS_Reset, p, v, 0, 0); }
int _ss_lock(int p, void *v) { return cmoc_os_setstat(SS_Lock, p, v, 0, 0); }
int _ss_attr(int p, void *v) { return cmoc_os_setstat(SS_Attr, p, v, 0, 0); }
int _ss_rel(int p) { return cmoc_os_ss_relea(p); }
int _ss_size(int p, void *hi, void *lo) {
  return cmoc_os_setstat(SS_Size, p, hi, lo, 0);
}
