/* Run under OS-9; exercises real kernel calls, not the host mocks. */
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>
#include "cmoc_os9.h"

void __cmoc_snapshot(registers_6809 *);
void *__cmoc_data_base(void);

int main(void)
{
    uid_t uid = getuid();
    char filename[] = "ostestXXXXXX";
    char line[8];
    int fd, failed = 0, read_failed = 0;
    if (uid == (uid_t)-1 || asetuid((unsigned int)uid) != 0 || getuid() != uid) {
        printf("identity [FAIL] errno=%d\n", errno);
        return 1;
    }
    puts("identity [PASS]");
    {
        registers_6809 regs;
        memset(&regs, 0, sizeof regs);
        regs.y = 0xa55a;
        if (cmoc_os_syscall(F$ID, &regs) != 0 || regs.y != (unsigned)uid) {
            puts("syscall register copy [FAIL]");
            failed = 1;
        } else
            puts("syscall register copy [PASS]");
        memset(&regs, 0xa5, sizeof regs);
        __cmoc_snapshot(&regs);
        if (regs.x != (uint16_t)(uintptr_t)&regs ||
            regs.u != (uint16_t)(uintptr_t)__cmoc_data_base()) {
            puts("register snapshot [FAIL]");
            failed = 1;
        } else
            puts("register snapshot [PASS]");
    }
    fd = mkstemp(filename);
    if (fd < 0) {
        printf("temporary file [FAIL] errno=%d\n", errno);
        return 1;
    }
    if (write(fd, "hi\r", 3) != 3 || lseek(fd, 0, SEEK_SET) != 0 ||
        readln(fd, line, sizeof line) != 3 ||
        line[0] != 'h' || line[1] != 'i' || line[2] != '\n' ||
        readln(fd, line, sizeof line) != 0)
        read_failed = 1;
    close(fd);
    unlink(filename);
    puts(read_failed ? "readln [FAIL]" : "readln [PASS]");
    return failed | read_failed;
}
