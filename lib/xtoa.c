#include <stdlib.h>

static void
utoa_core(unsigned value, char *buffer)
{
    char digits[5];
    int count = 0;
    do {
        digits[count++] = (char) ((value % 10U) + '0');
        value /= 10U;
    } while (value);
    while (count)
        *buffer++ = digits[--count];
    *buffer = 0;
}

char *
utoa(unsigned value, char *buffer)
{
    utoa_core(value, buffer);
    return buffer;
}

char *
utoa10(unsigned value, char *buffer)
{
    return utoa(value, buffer);
}

char *
itoa(int value, char *buffer)
{
    char *digits = buffer;
    unsigned magnitude = (unsigned) value;
    if (value < 0) {
        *digits++ = '-';
        magnitude = 0U - magnitude;
    }
    utoa_core(magnitude, digits);
    return buffer;
}

char *
itoa10(int value, char *buffer)
{
    return itoa(value, buffer);
}
