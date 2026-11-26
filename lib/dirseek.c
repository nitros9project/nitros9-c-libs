#include <dir.h>
#include <stdio.h>
#include <unistd.h>

void
seekdir(DIR *dirp, long location)
{
    lseek(dirp->dd_fd, location, SEEK_SET);
}

long
telldir(DIR *dirp)
{
    return lseek(dirp->dd_fd, 0L, SEEK_CUR);
}
