#include <ctype.h>

/* Both targets have 16-bit unsigned words and big-endian 32-bit longs.
 * Accumulate as two words: C3 has no unsigned-long arithmetic type. */
union number32 {
    unsigned long value;
    unsigned word[2];
};

static int
digit_value(int ch)
{
    if (ch >= '0' && ch <= '9') return ch - '0';
    if (ch >= 'a' && ch <= 'z') return ch - 'a' + 10;
    if (ch >= 'A' && ch <= 'Z') return ch - 'A' + 10;
    return -1;
}

static int
parse_number(const char *text, char **end, int base, union number32 *value,
             int *negative)
{
    const char *p = text;
    int digit, any = 0, overflow = 0;
    long product;
    unsigned carry;
    value->word[0] = value->word[1] = 0;
    *negative = 0;
    while (*p && (((unsigned) *p) & 255) < 128 && isspace(*p)) p++;
    if (*p == '+' || *p == '-') {
        *negative = *p == '-';
        p++;
    }
    if ((base == 0 || base == 16) && p[0] == '0' &&
        (p[1] == 'x' || p[1] == 'X') &&
        digit_value(p[2]) >= 0 && digit_value(p[2]) < 16) {
        p += 2;
        base = 16;
    } else if (base == 0)
        base = *p == '0' ? 8 : 10;
    if (base >= 2 && base <= 36) {
        while ((digit = digit_value(*p)) >= 0 && digit < base) {
            any = 1;
            if (!overflow) {
                product = (long) value->word[1] * base + digit;
                value->word[1] = (unsigned) product;
                carry = (unsigned) (product >> 16);
                product = (long) value->word[0] * base + carry;
                if (product > 65535L)
                    overflow = 1;
                else
                    value->word[0] = (unsigned) product;
            }
            p++;
        }
    }
    if (end) *end = (char *) (any ? p : text);
    if (overflow) value->word[0] = value->word[1] = 65535U;
    return overflow;
}

unsigned long
strtoul(const char *text, char **end, int base)
{
    union number32 value;
    int negative;
    int overflow = parse_number(text, end, base, &value, &negative);
    if (negative && !overflow) {
        value.word[0] = ~value.word[0];
        value.word[1] = 0U - value.word[1];
        if (!value.word[1]) value.word[0]++;
    }
    return value.value;
}

long
strtol(const char *text, char **end, int base)
{
    union number32 value;
    int negative;
    int overflow = parse_number(text, end, base, &value, &negative);
    if (negative) {
        if (overflow || value.word[0] > 32768U ||
            (value.word[0] == 32768U && value.word[1])) {
            value.word[0] = 32768U;
            value.word[1] = 0;
        }
        value.word[0] = ~value.word[0];
        value.word[1] = 0U - value.word[1];
        if (!value.word[1]) value.word[0]++;
    } else if (overflow || value.word[0] > 32767U) {
        value.word[0] = 32767U;
        value.word[1] = 65535U;
    }
    return (long) value.value;
}
