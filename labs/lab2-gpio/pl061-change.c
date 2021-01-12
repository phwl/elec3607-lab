/*
**    pl061-change.c     - display changes to the GPIO_GPIODATA state
*/

#include <stdio.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <time.h>

#define GPIO0_START_ADDR 0x09030000
#define GPIO0_END_ADDR   0x09030fff
#define GPIO0_SIZE (GPIO0_END_ADDR - GPIO0_START_ADDR)

#define GPIO_GPIODATA    0

/* high resolution time stamp */
double
gethrtime()
{
    int    r;
    int64_t    ts;
    struct timespec t;

    /* read the time stamp */
    r = clock_gettime(CLOCK_MONOTONIC, &t);
    ts = (int64_t)(t.tv_sec) * (int64_t)1000000000 + (int64_t)(t.tv_nsec);
    return ts / 1.0e9;
}

int
main()
{
    volatile void *gpio_addr;
    volatile unsigned char *gpio_gpiodata_addr;
    unsigned char        c, oldc;

    int fd = open("/dev/mem", O_RDWR);
    gpio_addr = mmap(0, GPIO0_SIZE, PROT_READ | PROT_WRITE, 
            MAP_SHARED, fd, GPIO0_START_ADDR);

    gpio_gpiodata_addr   = gpio_addr + GPIO_GPIODATA + 0xff;

    
    oldc = c = *gpio_gpiodata_addr;

    for (;;)
    {
        c = *gpio_gpiodata_addr;
        if (c != oldc)
        {
            oldc = c;
            printf("GPIODATA=%x (t=%fs)\n", c, gethrtime());
        }
    }
}
