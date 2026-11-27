/*===-- os9.h - Canonical OS-9 kernel-call interface -------------*- C -*-===
 *
 * Part of LLVM-MC6809, under the Apache License v2.0 with LLVM Exceptions.
 * See https://llvm.org/LICENSE.txt for license information.
 * SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
 *
 * Native entries are assembled from nitros9-c-libs assembly sources for the selected
 * compiler ABI. This header contains declarations and source aliases, not
 * inline syscall implementations or runtime ABI adapters.
 *
 *===----------------------------------------------------------------------===*/

#ifndef __MC6809_OS9_H__
#define __MC6809_OS9_H__
#define NITROS9_OS_CALLS_ABI 1

#ifdef __cplusplus
extern "C" {
#endif

/* Function codes (os9.d names without the `$`). */
#define OS9_F_LINK   0x00
#define OS9_F_LOAD   0x01
#define OS9_F_UNLINK 0x02
#define OS9_F_EXIT   0x06
#define OS9_F_MEM    0x07
#define OS9_F_SLEEP  0x0A
#define OS9_F_ID     0x0C
#define OS9_F_TIME   0x15
#define OS9_F_TPS    0x25 /* Level 2 */
#define OS9_F_XTIME  0x56 /* Level 2 */
#define OS9_I_DUP    0x82
#define OS9_I_CREATE 0x83
#define OS9_I_OPEN   0x84
#define OS9_I_MAKDIR 0x85
#define OS9_I_CHGDIR 0x86
#define OS9_I_DELETE 0x87
#define OS9_I_SEEK   0x88
#define OS9_I_READ   0x89
#define OS9_I_WRITE  0x8A
#define OS9_I_READLN 0x8B
#define OS9_I_WRITLN 0x8C
#define OS9_I_GETSTT 0x8D
#define OS9_I_SETSTT 0x8E
#define OS9_I_CLOSE  0x8F

/* I$GetStt / I$SetStt function codes (SS.* in os9.d). */
#define OS9_SS_OPT   0x00 /* get/set the 32-byte path options */
#define OS9_SS_READY 0x01 /* data ready? */
#define OS9_SS_SIZE  0x02 /* file size (X:U); set = truncate/extend */
#define OS9_SS_POS   0x05 /* file position (X:U) */
#define OS9_SS_EOF   0x06 /* at end of file? */
#define OS9_SS_DEVNM 0x0E /* device name */
#define OS9_SS_FD    0x0F /* file descriptor sector */

/* Error codes this header interprets itself (the rest are in os9.d). */
#define OS9_E_PTHFUL 0xC8
#define OS9_E_BPNUM  0xC9
#define OS9_E_BMODE  0xCB
#define OS9_E_MEMFUL 0xCF
#define OS9_E_UNKSVC 0xD0
#define OS9_E_EOF    0xD3
#define OS9_E_NES    0xD5
#define OS9_E_FNA    0xD6
#define OS9_E_BPNAM  0xD7
#define OS9_E_PNNF   0xD8
#define OS9_E_SLF    0xD9
#define OS9_E_CEF    0xDA
#define OS9_E_IBA    0xDB
#define OS9_E_HANGUP 0xDC
#define OS9_E_MNF    0xDD
#define OS9_E_DELSP  0xDF
#define OS9_E_IPRCID 0xE0
#define OS9_E_NOCHLD 0xE2
#define OS9_E_KWNMOD 0xE7
#define OS9_E_NEMOD  0xEA
#define OS9_E_BNAM   0xEB
#define OS9_E_NORAM  0xED
#define OS9_E_DNE    0xEE /* directory not empty */
#define OS9_E_NOTASK 0xEF
#define OS9_E_UNIT   0xF0
#define OS9_E_SECT   0xF1
#define OS9_E_WP     0xF2
#define OS9_E_CRC    0xF3
#define OS9_E_READ   0xF4
#define OS9_E_WRITE  0xF5
#define OS9_E_NOTRDY 0xF6
#define OS9_E_SEEK   0xF7
#define OS9_E_FULL   0xF8
#define OS9_E_BTYP   0xF9
#define OS9_E_DEVBSY 0xFA
#define OS9_E_DIDC   0xFB
#define OS9_E_LOCK   0xFC
#define OS9_E_SHARE  0xFD
#define OS9_E_DEADLK 0xFE

/* I$Open / I$Create access modes and file attributes (same bits). */
#define OS9_READ     0x01
#define OS9_WRITE    0x02
#define OS9_UPDATE   (OS9_READ | OS9_WRITE)
#define OS9_EXEC     0x04
#define OS9_PREAD    0x08
#define OS9_PWRITE   0x10
#define OS9_PEXEC    0x20
#define OS9_SHARE    0x40
#define OS9_DIR      0x80

/* The OS-9 error code of the last failed call (the C library's errno when
 * one is linked; libclang_rt.os9.a carries a weak definition for programs
 * without one).  Lives in the process data area like every other writable
 * object. */
extern int errno;

/*
 * OS9_SYSCALL(code, (outputs), (inputs))
 *
 * The system call itself: `os9 code` with the given asm operand lists, each
 * wrapped in one pair of parentheses.  Register constraints: A, B, d (D),
 * x, y; "c" is the carry flag (1 = the call failed, B holds the error code).
 * U and DP are the process data-area base and must not be named.  Memory is
 * assumed clobbered, so buffers the kernel reads or writes need no further
 * annotation.
 *
 *   unsigned char err, code;
 *   OS9_SYSCALL(OS9_I_CLOSE, ("=c"(err), "=B"(code)), ("A"(path)));
 *
 * Two operands must never name overlapping registers -- B and D together,
 * say: they are the same register, and asking for both leaves the allocator
 * nothing to satisfy them with.
 *
 * A call that hands back the pair D has no accumulator left for the carry,
 * which needs a byte register to be read into: use OS9_SYSCALL_BERR for
 * those, which reports the failure in B instead.
 */

#define __OS9_UNPAREN(...) __VA_ARGS__
/* A parenthesised operand list, comma-terminated when it has anything in it,
 * so another operand can always follow. */
#define __OS9_LIST(...) __VA_OPT__(__VA_ARGS__,)
#define OS9_SYSCALL(code, outputs, inputs)                                    \
  __asm__ __volatile__("os9 %c[__os9_code]"                                   \
                       : __OS9_UNPAREN outputs                                \
                       : __OS9_LIST inputs [__os9_code] "i"(code)             \
                       : "memory")

/*
 * OS9_SYSCALL_BERR(code, outputs, inputs)
 *
 * As OS9_SYSCALL, but the failure arrives in B -- the OS-9 error code, or
 * zero when the call worked -- and the carry is not asked for at all.  The
 * calls that hand back the pair D have no accumulator to spare for the
 * carry, and one asked for anyway is an allocation with no answer: the two
 * bytes A and B are the only homes there are, and the call's own result is
 * in both of them.
 *
 * Nothing is lost by clearing B on the way out.  For F$Mem the kernel
 * already returns a whole number of 256-byte pages, so the low byte of the
 * size is zero; for I$Create B carries nothing once the call has worked.
 */
#define OS9_SYSCALL_BERR(code, outputs, inputs)                               \
  __asm__ __volatile__("os9 %c[__os9_code]\n\t"                              \
                       "bcs .Los9err%=\n\t"                                  \
                       "clrb\n"                                              \
                       ".Los9err%=:"                                          \
                       : __OS9_UNPAREN outputs                                \
                       : __OS9_LIST inputs [__os9_code] "i"(code)             \
                       : "memory")

#include <os9raw.h>
#define __os9_xu n9_xu
#define __os9_seek n9_seek
#define __os9_getstt_xu n9_getstt_xu
#define __os9_setstt_xu n9_setstt_xu
#define __os9_link n9_link
#define __os9_load n9_load
#define __os9_unlink n9_unlink
#define _os_create n9_create
#define _os_delete n9_delete
#define _os_chgdir n9_chgdir
#define _os_dup n9_dup
#define _os_getstt_buf n9_getstt_buf
#define _os_setstt_buf n9_setstt_buf
#define _os_getstt n9_getstt
#define _os_mem n9_mem
#define _os_id n9_id
#define _os_sleep n9_sleep
#define _os_time _os_getime
int _os_open(const char *, int, int *);
int _os_close(int);
int _os_makdir(const char *, int);
int _os_read(int, void *, int *);
int _os_readln(int, void *, int *);
int _os_write(int, const void *, int *);
int _os_writeln(int, const void *, int *);
int _os_getime(void *);

/* Compatibility for callers explicitly translating a native error. */
#define __os9_fail(code) (errno = (unsigned char)(code))

/* The C runtime's view of the process, set up by the start-up code before
 * main(): the heap sbrk() hands out, and the program's own name (the
 * module name, argv[0]). */
extern char *__os9_heap_cur;   /* next free byte */
extern char *__os9_heap_end;   /* one past the last usable byte */
extern char  __os9_progname[]; /* NUL-terminated module name */

/* Out-of-line entry points, in libclang_rt.os9.a: _exit, and the
 * byte-count-returning _read/_write (-1 on failure, errno set) under their
 * POSIX-style and NitrOS-9 names (`$` in an identifier needs
 * -fdollars-in-identifiers, which the mc6809-unknown-os9 driver enables;
 * define OS9_NO_DOLLAR_NAMES to hide them).  A C library's read()/write()
 * are separate functions built on the shims. */
void _exit(int __status) __attribute__((__noreturn__));
int  _write(int __fd, const void *__buf, int __n);
int  _read(int __fd, void *__buf, int __n);

#ifndef OS9_NO_DOLLAR_NAMES
#ifndef F$Exit
void F$Exit(int __status) __attribute__((__noreturn__));
#endif
#ifndef I$Write
int  I$Write(int __fd, const void *__buf, int __n);
#endif
#ifndef I$Read
int  I$Read(int __fd, void *__buf, int __n);
#endif
#endif /* !OS9_NO_DOLLAR_NAMES */

#ifdef __cplusplus
}
#endif

#endif /* __MC6809_OS9_H__ */
