/*
 * **    blink.c -    blink with 1s delay 
 * */

#include <stdio.h>
#include <unistd.h>
#include <gpiod.h>

#define GPIOCHIP        1
#define GPIOLINE        24

int 
main(int argc, char *argv[])
{
        struct gpiod_chip *output_chip;
        struct gpiod_line *output_line;
        int line_value;

        /* open chip and get line */
        output_chip = gpiod_chip_open_by_number(GPIOCHIP);
        output_line = gpiod_chip_get_line(output_chip, GPIOLINE);

        /* config as output and set a description */
        gpiod_line_request_output(output_line, "blink",
                GPIOD_LINE_ACTIVE_STATE_HIGH);

        for (;;)
        {
                line_value = !line_value;
                gpiod_line_set_value(output_line, line_value);
                sleep(1);
        }

        return 0;
}

