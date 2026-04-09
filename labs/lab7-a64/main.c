#include <stdlib.h>

extern void printdec(int n);

int
main()
{
    srand(0);
    for (int i = 0; i < 10; i++)
    {
        int r = rand();

        printdec(r);
    }
    return 0;
}

