#include <time.h>

extern time_t _mkutc(struct tm *tp);

time_t
o2utime(_os_time *packet)
{
    struct tm broken;
    broken.tm_year = ((unsigned) packet->year) & 255;
    broken.tm_mon = (((unsigned) packet->month) & 255) - 1;
    broken.tm_mday = ((unsigned) packet->day) & 255;
    broken.tm_hour = ((unsigned) packet->hours) & 255;
    broken.tm_min = ((unsigned) packet->minutes) & 255;
    broken.tm_sec = ((unsigned) packet->seconds) & 255;
    return _mkutc(&broken);
}

time_t
time(time_t *destination)
{
    _os_time packet;
    time_t value;
    if (_os_getime(&packet))
        return -1L;
    value = o2utime(&packet);
    if (destination)
        *destination = value;
    return value;
}

void
u2otime(_os_time *packet, struct tm *broken)
{
    packet->year = broken->tm_year;
    packet->month = broken->tm_mon + 1;
    packet->day = broken->tm_mday;
    packet->hours = broken->tm_hour;
    packet->minutes = broken->tm_min;
    packet->seconds = broken->tm_sec;
}
