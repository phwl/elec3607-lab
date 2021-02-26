/*
 * ssd.c -    count up and down on the SSD
 * 
*/

#include <stdio.h>
#include <unistd.h>
#include <gpiod.h>

/* the SSD is entirely on this chip */
#define OUT_GPIOCHIP	0

/* the S2 button on the BBG */
#define	IN_GPIOCHIP		2
#define	IN_GPIOLINE		8

#define	NELTS(x)	(sizeof(x) / sizeof(x[0]))  // calculate number of elements in x
#define	SEGMENTS	NELTS(gpiossd)

static int	gpiossd[] = { 2, 13, 12, 4, 5, 15, 31 };

/* FILL THIS IN */
static int	ssd[][SEGMENTS] = {
	{ 1, 1, 1, 1, 1, 1, 0 },	/* 0 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 1 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 2 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 3 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 4 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 5 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 6 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 7 */
	{ 0, 0, 0, 0, 0, 0, 0 },	/* 8 */
	{ 0, 0, 0, 0, 0, 0, 0 } };	/* 9 */

int 
main(int argc, char *argv[])
{
    struct	gpiod_chip *output_chip;
    struct	gpiod_line *output_line[SEGMENTS];
	struct	gpiod_chip *input_chip;
	struct	gpiod_line *input_line;
    int		line_value;
	int		i, j;

	/* open input */
	input_chip = gpiod_chip_open_by_number(IN_GPIOCHIP);
	input_line = gpiod_chip_get_line(input_chip, IN_GPIOLINE);
	gpiod_line_request_input(input_line, "ssd");

    /* open /dev/gpiochip0 */
    output_chip = gpiod_chip_open_by_number(OUT_GPIOCHIP);
	for (i = 0; i < SEGMENTS; i++)
	{
		output_line[i] = gpiod_chip_get_line(output_chip, gpiossd[i]);
		/* config as output and set a description */
		gpiod_line_request_output(output_line[i], "ssd", GPIOD_LINE_ACTIVE_STATE_HIGH);
	}

	int d = 0;		/* the digit to display */
	for (;;) 
	{
		/* display all segments */
		for (j = 0; j < SEGMENTS; j++)
		{
            /* FILL THIS IN */
		}
        	sleep(1);
		/* update count */

        /* FILL THIS IN */
	}
    return 0;
}

