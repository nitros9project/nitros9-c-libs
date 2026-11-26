#include <ctype.h>

#undef isdigit
#undef isalpha
#undef isprint
#undef isspace
#undef toupper
#undef tolower

int
isdigit(int c)
{
    return _chcodes[c] & _DIGIT;
}

int
isalpha(int c)
{
    return _chcodes[c] & (_UPPER | _LOWER);
}

int
isprint(int c)
{
    return _chcodes[c] & (_PUNCT | _UPPER | _LOWER | _DIGIT);
}

int
isspace(int c)
{
    return _chcodes[c] & _WHITE;
}

int
toupper(int c)
{
    return c >= 'a' && c <= 'z' ? c - ('a' - 'A') : c;
}

int
tolower(int c)
{
    return c >= 'A' && c <= 'Z' ? c + ('a' - 'A') : c;
}
