/*
**    Blinky under QEMU and libgpiod
*/

#include <stdio.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#include <gpiod.h>
#include <time.h>
 
#define CONSUMER "gpiod-lab"        /* this identifies the consumer */
#define NUM_THREADS 2               /* we have one writer and one reader */
#define NSPERIOD    200000000ULL    /* output period in ns */

pthread_mutex_t mutexline;          /* only reader or writer can access line */
 
/* create thread argument struct for thr_func() */
typedef struct _thread_data_t 
{
    int tid;
    struct gpiod_line *gpioline;
} thread_data_t;
 
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

/*
**    Display edges 
*/
void
gpio_reader(struct gpiod_line *line)
{
    struct timespec timeout = { 0, NSPERIOD / 100ULL };
    struct timespec shortdelay = { 0, NSPERIOD / 100ULL };
    struct timespec rem;
    int    r, v;
    int    event = 0;

    for (;;)
    {
        /* get exclusive access to the line */
        pthread_mutex_lock (&mutexline);

        /* get line */
        if (r = gpiod_line_request_both_edges_events(line, CONSUMER))
            goto release;

        /* wait for an event */
        r = gpiod_line_event_wait(line, &timeout);
        if (r > 0)    /* success */
        {
            /* read the gpio pin value */
            v = gpiod_line_get_value(line);
            printf("Event %d: Pin=%d at t=%fs\n", ++event, v, gethrtime());
        }

        /* release the line */
    release:
        gpiod_line_release(line);
        pthread_mutex_unlock (&mutexline);
        nanosleep(&shortdelay, &rem);
    }
}

/*
**    Blink a number of times
*/
void
gpio_writer(struct gpiod_line *line)
{
    struct timespec delay = { 0, NSPERIOD / 2 };
    struct timespec rem;
    int    v = 0;
    int    r;

    for (int i = 0; i < 10; i++)
    {
        /* get exclusive access to the line */
        pthread_mutex_lock (&mutexline);
        /* config as output and set a description */
        if (r = gpiod_line_request_output(line, CONSUMER, v))
            goto release;

        /* toggle output */
        v = !v;
        gpiod_line_set_value(line, v);

        /* release line */
    release:
        gpiod_line_release(line);
        pthread_mutex_unlock (&mutexline);
        nanosleep(&delay, &rem);
    }
}

/* 
**    Create pthreads - the thread created will either be a reader or writer 
*/
void *thr_func(void *arg) {
    thread_data_t *data = (thread_data_t *)arg;
 
    switch(data->tid) 
    {
        case 0: /* writer */
            gpio_writer(data->gpioline);
            break;
        default: /* reader */
            gpio_reader(data->gpioline);
            break;
    }
 
    pthread_exit(NULL);
}
 
int 
main(int argc, char **argv) 
{
    pthread_t thr[NUM_THREADS];
    pthread_attr_t attr;
    int i, r;
    /* create a thread_data_t argument array */
    thread_data_t thr_data[NUM_THREADS];

    /* gpio structures */
    struct gpiod_chip *output_chip;
    struct gpiod_line *output_line;

    /* open /dev/gpiochip0 */
    output_chip = gpiod_chip_open_by_number(0);
    
    /* work on pin 3 */
    output_line = gpiod_chip_get_line(output_chip, 3);

    /* create threads */
    pthread_mutex_init(&mutexline, NULL);
    for (i = 0; i < NUM_THREADS; ++i) 
    {
        thr_data[i].tid = i;
        thr_data[i].gpioline = output_line;
        assert(pthread_create(&thr[i], NULL, thr_func, &thr_data[i]) == 0);
    }
    /* block until thread 0 completes */
    pthread_join(thr[0], NULL);
    fflush(stdout);
 
    return EXIT_SUCCESS;
}
