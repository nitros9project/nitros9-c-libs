#include <stdlib.h>

typedef int (*compare_fn)(const void *, const void *);

void *
bsearch(const void *key, const void *base, size_t count, size_t size,
        compare_fn compare)
{
    const char *first = (const char *) base;
    const char *middle;
    size_t half;
    int order;
    while (count) {
        half = count / 2;
        middle = first + half * size;
        order = (*compare)(key, middle);
        if (!order)
            return (void *) middle;
        if (order > 0) {
            first = middle + size;
            count -= half + 1;
        } else
            count = half;
    }
    return 0;
}
