/*
**        Blinky under QEMU and libgpiod
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
    int ssdtable[] = {	// seven segment display patterns for each digit
        0bXXX, // 0
        0bXXX, // 1
        0bXXX, // 2
        0bXXX, // 3
        0bXXX, // 4
        0bXXX, // 5
        0bXXX, // 6
        0bXXX, // 7
        0bXXX, // 8
        0bXXX  // 9
    }; 

    // infinite loop incrementing i
    for (int i = 0;; i++) {
        int digit = i % NELTS(ssdtable);	// this is the digit to display

        mutex_start();			// ignore this, it's to do the graphics

	// Loop over all the seven segments to the display to draw digit
        for (int j = 0; j < LINES; j++) {
            /* config as output and set a description */
            if (!(r = gpiod_line_request_output(output_lines[j], CONSUMER, v))) {
                v = XXX;		// the binary value to write to line j
                XXX(output_lines[j], v);
            }
            gpiod_line_release(output_lines[j]);
        }
        mutex_stop();			// ignore this, it's to do the graphics
        usleep(USPERIOD);
    }
}
