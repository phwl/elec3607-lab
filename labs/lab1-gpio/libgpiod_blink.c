/*
**    Blink using libgpiod
*/

#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
#include <gpiod.h>
 
#define LINES		1
#define	USPERIOD	1000
struct gpiod_line * output_lines[LINES];

void
gpio_init() {
    int i;
    int pins[] = { 26 };		// operate on all these pins

    /* gpio structures */
    struct gpiod_chip * output_chip;

    /* open /dev/gpiochip0 */
    output_chip = gpiod_chip_open_by_number(0);
    if (output_chip == NULL)
    {
        perror("gpiod_chip_open_by_number(0)");
        exit(1);
    }

    /* work on the pins specified in the pins array */
    for (i = 0; i < LINES; i++)
    {
        output_lines[i] = XXX;
        gpiod_line_request_output(output_lines[i], "blink", GPIOD_LINE_ACTIVE_STATE_HIGH);
    }

}

/*
 **        Blink a number of times
 */
void *
gpio_writer() {
    int v = 0;
    
    // infinite loop incrementing i
    for (int i = 0;; i++) {
        v = !v;			// this toggles between 1 and 0
	// we are going to blink all the lines 
        for (int j = 0; j < LINES; j++) {
            XXX;	// write v to line j
        }
    }
}

int
main(int arhv, char *argv[])
{
	gpio_init();
	gpio_writer();
}
