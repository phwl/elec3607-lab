/*
**	ELEC3607 gpio register interface example
*/

#include <assert.h>
#include <fcntl.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>

// GPIO which we want to toggle in this example.
#define OUTPUTPIN 26

// GPIO offset locations
#define PAGE_SIZE 4096
#define GPIO_SET_OFFSET 0x1C
#define GPIO_CLR_OFFSET 0x28

void 
gpio_setasoutput(volatile uint32_t *gpio_p, int b) {
	*(gpio_p + (b/10)) &= ~(7 << ((b%10)*3));  // prepare: set as input
	*(gpio_p + (b/10)) |=  (1 << ((b%10)*3));  // set as output.
}

int 
main(int argc, char *argv[]) {
	int			mem_fd;
	uint32_t	*gpio_p;
	volatile uint32_t *set_reg;
	volatile uint32_t *clr_reg;

	if ((mem_fd = open("/dev/gpiomem", O_RDWR|O_SYNC) ) < 0) {
		perror("can't open /dev/gpiomem: ");
		exit(0);
	}
	gpio_p = (uint32_t *)mmap(NULL, PAGE_SIZE, PROT_READ|PROT_WRITE,  
							MAP_SHARED, mem_fd, 0);
	gpio_setasoutput(gpio_p, OUTPUTPIN);

	set_reg = gpio_p + (GPIO_SET_OFFSET / sizeof(uint32_t));
	clr_reg = gpio_p + (GPIO_CLR_OFFSET / sizeof(uint32_t));

	for (;;) {
        XXX;
	}
    exit(0);
}
