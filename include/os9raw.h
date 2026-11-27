#ifndef NITROS9_OS9RAW_H
#define NITROS9_OS9RAW_H
/* Raw kernel contracts shared by compiler runtimes. n9_create preserves the
 * LLVM header argument order; _os_create has the Kreider/CMOC order. Both
 * report an existing file without reopening or truncating it. */
struct n9_xu { unsigned char path, fn; unsigned long pos; };
struct __os9_module { const char *name; unsigned char type; void *header, *entry; };
int n9_create(const char *name, int mode, int attrs, int *path);
int n9_delete(const char *name);
int n9_chgdir(const char *name, int mode);
int n9_dup(int path, int *newpath);
int n9_getstt_buf(int path, int fn, void *buf, int count);
int n9_setstt_buf(int path, int fn, const void *buf, int count);
int n9_getstt(int path, int fn);
int n9_mem(unsigned size, unsigned *actual, void **top);
int n9_id(int *pid, int *uid);
int n9_sleep(unsigned ticks);
void n9_exit(int status);
int n9_prerr(int path, int error);
int n9_icpt(void *entry, void *data);
int n9_seek(struct n9_xu *position);
int n9_getstt_xu(struct n9_xu *position);
int n9_setstt_xu(struct n9_xu *position);
int n9_link(struct __os9_module *module);
int n9_load(struct __os9_module *module);
int n9_unlink(void *module);
#endif
