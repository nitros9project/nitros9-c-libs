#include <stdlib.h>

char *
ltoa(long value, char *buffer)
{
    char digits[11];
    char *out = buffer;
    int count = 0;
    int negative = value < 0;
    /* Keep the magnitude negative so LONG_MIN is representable. */
    if (value > 0)
        value = -value;
    do {
        digits[count++] = (char) ('0' - (int) (value % 10L));
        value /= 10L;
    } while (value);
    if (negative)
        *out++ = '-';
    while (count)
        *out++ = digits[--count];
    *out = 0;
    return buffer;
}
