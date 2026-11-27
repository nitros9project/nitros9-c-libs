#ifndef CMOC_OS9_LLVM_SYSCALLS_H
#define CMOC_OS9_LLVM_SYSCALLS_H
int cmoc_os_getuid(int *uid);
int cmoc_os_asetuid(int uid);
int cmoc_os_readln(int path, void *buffer, int *count);
/* Source aliases to native entries; no runtime adapter functions. */
#define cmoc_os9_get_user cmoc_os_getuid
#define cmoc_os9_set_user cmoc_os_asetuid
#define cmoc_os9_read_line cmoc_os_readln
#endif
