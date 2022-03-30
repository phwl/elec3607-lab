#define CONSUMER "gpiod-lab"	// this identifies the consumer 
#define USPERIOD 1000000	// output period in us 
#define LINES 7			// number of gpio lines to control
#define NELTS(a) (sizeof(a) / sizeof(a[0]))	// returns # elts in a

extern pthread_mutex_t mutexline; /* only reader or writer can access line */
extern struct gpiod_line * output_lines[LINES];
extern void mutex_start(), mutex_stop();

extern void gpio_init();
extern void *gpio_writer(void * ignored);
