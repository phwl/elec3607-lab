/*
**    blink.c -    blink gpiochip0 line 3 with delay given by either
**                 the command line or the default (NSPERIOD)
*/

#include <stdio.h>
#include <unistd.h>
#include <gpiod.h>

#define NSPERIOD    200000000ULL    /* output period in ns */

int 
main(int argc, char *argv[])
{
    struct gpiod_chip *output_chip;
    struct gpiod_line *output_line;
    struct timespec delay = {0, NSPERIOD};
    struct timespec rem;
    int line_value;

    if (argc == 2)
        delay.tv_nsec = atoll(argv[1]);

    /* open /dev/gpiochip0 */
    output_chip = gpiod_chip_open_by_number(0);
    
    /* work on pin 3 */
    output_line = gpiod_chip_get_line(output_chip, 3);

    /* config as output and set a description */
    gpiod_line_request_output(output_line, "blink",
                  GPIOD_LINE_ACTIVE_STATE_HIGH);

    for (int i = 0; i < 10; i++)
    {
        line_value = !line_value;
        gpiod_line_set_value(output_line, line_value);
            nanosleep(&delay, &rem);
    }
    
    return 0;
}
