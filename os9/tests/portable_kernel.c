/* Exercise the same native OS-call contracts with CMOC, C3, and LLVM. */
#include <os.h>
#include <os9raw.h>
#include <stdio.h>
#include <errno.h>
#include <string.h>
#define PHASE(s) do { puts(s); fflush(stdout); } while (0)
#define CHECK(c) do { if (!(c)) { printf("FAIL %d errno %d\r", __LINE__,errno); return 1; }} while(0)
int main()
{
    int fd, n, copy, pid, uid, status, child;
    registers_6809 regs;
    unsigned actual;
    void *top, *module;
    char buffer[8], options[32], error_byte;
    struct n9_xu position;
    struct __os9_module image;
    PHASE("identity");
    memset(&regs, 0, sizeof(regs));
    CHECK(_os_syscall(F$ID, &regs) == 0 && regs.a > 0);
    regs.a = 255;
    error_byte = E$BPNum;
    status = _os_syscall(I$Close, &regs);
    if (status != E$BPNum || regs.b != error_byte || errno != E$BPNum) {
        printf("syscall error result=%d B=%d expected=%d errno=%d tests=%d/%d/%d\r", status, regs.b, error_byte, errno, status == E$BPNum, regs.b == error_byte, errno == E$BPNum);
        fflush(stdout);
    }
    CHECK(status == E$BPNum && regs.b == error_byte && errno == E$BPNum);
    CHECK(n9_id(&pid, &uid) == 0 && pid > 0);
    if (uid == 0) {
        CHECK(_os_asetuid(uid) == 0);
        CHECK(_os_setuid(uid) == 0);
    }
    CHECK(n9_mem(0, &actual, &top) == 0 && actual > 0 && top != 0);
    PHASE("file I/O");
    CHECK(n9_create("N9TEST", 3, 11, &fd) == 0);
    CHECK(n9_create("N9TEST", 3, 11, &copy) == E$CEF);
    CHECK(_os_create("N9TEST", 3, &copy, 11) == E$CEF);
    n = 5;
    CHECK(_os_write(fd, "hello", &n) == 0 && n == 5);
    n = 0;
    CHECK(_os_write(fd, "", &n) == 0 && n == 0);
    CHECK(n9_dup(fd, &copy) == 0 && _os_close(copy) == 0);
    position.path = fd;
    position.fn = SS_Pos;
    position.pos = 0;
    CHECK(n9_getstt_xu(&position) == 0 && position.pos == 5);
    position.pos = 0;
    CHECK(n9_seek(&position) == 0);
    n = 5;
    CHECK(_os_read(fd, buffer, &n) == 0 && n == 5 && memcmp(buffer, "hello", 5) == 0);
    n = 5;
    CHECK(_os_read(fd, buffer, &n) == 0 && n == 0);
    CHECK(n9_getstt_buf(fd, SS_Opt, options, 32) == 0 && options[0] == 1);
    CHECK(_os_seek(fd, 0L) == 0);
    n = 5;
    CHECK(_os_readln(fd, buffer, &n) == 0 && n == 5 && memcmp(buffer, "hello", 5) == 0);
    n = 5;
    CHECK(_os_readln(fd, buffer, &n) == 0 && n == 0);
    PHASE("32-bit seek");
    CHECK(_os_seek(fd, 0x10002L) == 0);
    n = 1;
    CHECK(_os_write(fd, "Z", &n) == 0 && n == 1);
    position.fn = SS_Size;
    CHECK(n9_getstt_xu(&position) == 0 && position.pos == 0x10003L);
    CHECK(_os_close(fd) == 0 && n9_delete("N9TEST") == 0);
    PHASE("module services");
    image.name = "n9kid";
    image.type = Prgrm | Objct;
    image.header = 0;
    image.entry = 0;
    CHECK(n9_load(&image) == 0 && image.header != 0 && image.entry != 0);
    CHECK(n9_unlink(image.header) == 0);
    CHECK(_os_modload("n9kid", Objct, Prgrm, &module) == 0);
    CHECK(_os_modunlink(module) == 0);
    PHASE("sleep");
    image.name = "NOSUCHMODULE";
    status = n9_load(&image);
    CHECK(status != 0);
    module = (void *)0x1234;
    CHECK(_os_modload("NOSUCHMODULE", Objct, Prgrm, &module) == status && errno == status && module == (void *)0x1234);
    CHECK(_os_modlink("NOSUCHMODULE", Objct, Prgrm, &module) == E$MNF && errno == E$MNF && module == (void *)0x1234);
    CHECK(n9_sleep(1) == 0);
    CHECK(_os_modlink("Shell", Objct, Prgrm, &module) == 0);
    CHECK(_os_modunlink(module) == 0);
    PHASE("fork/wait");
    CHECK(_os_fork("n9kid", 0, 0, Objct, Prgrm, 0, &child) == 0 && child > 0);
    CHECK(_os_wait(&status) == child && status == 7);
    PHASE("chain");
    CHECK(_os_fork("n9chain", 0, 0, Objct, Prgrm, 0, &child) == 0 && child > 0);
    CHECK(_os_wait(&status) == child && status == 7);
    CHECK(_os_wait(&status) == -1);
    CHECK(_os_open("NOSUCHFILE", 1, &fd) != 0);
    puts("N9 OS CALLS PASS");
    return 0;
}
