/*
**    Blinky under QEMU and libgpiod
*/

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#include <gpiod.h>
#include <time.h>
#include "gpio.h"
 
struct gpiod_line * output_lines[LINES];

void
gpio_init() {
    int i;
    int pins[] = { 0, 1, 2, 4, 5, 6, 7 };	// skip pin 3 on the qemu emulation

    /* gpio structures */
    struct gpiod_chip * output_chip;

    /* open /dev/gpiochip0 */
    output_chip = XXX(0);
    if (output_chip == NULL)
    {
        perror("gpiod_chip_open_by_number(0)");
        exit(1);
    }

    /* work on the pins specified in the pins array */
    for (i = 0; i < LINES; i++)
        output_lines[i] = XXX(output_chip, pins[i]);

}

/*
 **        Blink a number of times
 */
void *
gpio_writer(void * ignored) {
    int v = 0;
    int r;
    
    // infinite loop incrementing i
    for (int i = 0;; i++) {
        mutex_start();		// ignore this, it's to do the graphics

        v = !v;			// this toggles between 1 and 0
	// we are going to blink all the lines of the seven segment display
        for (int j = 0; j < LINES; j++) {
            if (!(r = gpiod_line_request_output(output_lines[j], CONSUMER, v))) {
                XXX(output_lines[j], v);	// write v to line j
            }
            gpiod_line_release(output_lines[j]);
        }
        mutex_stop();		// ignore this, it's to do the graphics
        usleep(USPERIOD);	// this delay is what makes it blink
    }
}
