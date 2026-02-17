
#include <assert.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>


#define OUTPUTPIN 24

#define AXI_GPIO_BASE 0x80030000UL

#define PAGE_SIZE 4096
#define GPIO_DATA 0x0
#define GPIO_TRI  0x4

int
main(int argc, char *argv[])
{
    int mem_fd;
    uint8_t *map_base;
    volatile uint32_t *gpio_p;

    // NOTE: /dev/gpiochip6 cannot be mmap'ed as registers. Use /dev/mem.
    if ((mem_fd = open("/dev/mem", O_RDWR | O_SYNC)) < 0) {
        perror("can't open /dev/mem");
        exit(1);
    }


    map_base = (uint8_t *)mmap(NULL, PAGE_SIZE, PROT_READ | PROT_WRITE,
                              MAP_SHARED, mem_fd,  AXI_GPIO_BASE);
    if (map_base == MAP_FAILED) {
        perror("mmap failed");
        close(mem_fd);
        exit(1);
    }
   
    gpio_p = (volatile uint32_t *)map_base;
    
    gpio_p[GPIO_TRI / 4] &= ~(1 << OUTPUTPIN); // set as output

    for (;;) {
        XXX;
    }

    // never reached
    munmap((void *)map_base, PAGE_SIZE);
    close(mem_fd);
    return 0;
}
