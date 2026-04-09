#include <stdio.h>

void
printdec(int n)
{
    while (n > 0)
    {
        int c = n % 10;
        putchar(c + '0');
        n /= 10;
    }
    putchar('\n');
}
