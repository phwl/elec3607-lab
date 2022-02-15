/*!
 * \brief A simple animation using cairo and GTK+ 
 *
 * This program shows high /usr/libexec/Xorg load while running full screen on Linux
 *
 * Compile with:
 *     gcc `pkg-config --cflags --libs gtk+-3.0` -lm -lpthread main.c
 *
 * or run: make -B all
 */

#include <unistd.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include <pthread.h>
#include <assert.h>
#include <gpiod.h>
#include <time.h>
#include <gtk/gtk.h>
#include "gpio.h"

pthread_mutex_t mutexline; /* only reader or writer can access line */

void
mutex_start() {
    /* get exclusive access to the line */
    pthread_mutex_lock( & mutexline);
}

void
mutex_stop() {
    pthread_mutex_unlock( & mutexline);
    usleep(100);
}

/* high resolution time stamp */
double
gethrtime() {
    int64_t ts;
    struct timespec t;

    /* read the time stamp */
    clock_gettime(CLOCK_MONOTONIC, &t);
    ts = (int64_t)(t.tv_sec) * (int64_t) 1000000000 + (int64_t)(t.tv_nsec);
    return ts / 1.0e9;
}

/* Local variables. */
static pthread_t drawing_thread;
static pthread_mutex_t mutex;
static cairo_surface_t * surface = NULL;
static int surface_width;
static int surface_height;

/* Local function prototypes. */
static gboolean invalidate_cb(void * );
static gboolean drawing_area_configure_cb(GtkWidget * , GdkEventConfigure * );
static void drawing_area_draw_cb(GtkWidget * , cairo_t * , void * );
static void * thread_draw(void * );

/*
 **        Display edges 
 */
unsigned char
gpio_state() {
    int r, v;
    int event = 0;
    static unsigned char old_state;
    unsigned char state = 0;

    mutex_start();

    /* get line */
    for (int j = 0; j < LINES; j++) {
        if (!(r = gpiod_line_request_input(output_lines[j], CONSUMER))) {
            v = gpiod_line_get_value(output_lines[j]);
            if (v)
                state |= (1 << j);
            else
                state &= ~(1 << j);
        }
        gpiod_line_release(output_lines[j]);
    }
    mutex_stop();
    if (state != old_state) {
        old_state = state;
        printf("Event %d: at t=%fs (state=%x)\n", ++event, gethrtime(), state);
    }
    return state;
}


int
main(int argc, char ** argv) {
    static pthread_t gpio_write_th;
    gtk_init( & argc, & argv);

    GtkWidget * main_window = gtk_window_new(GTK_WINDOW_TOPLEVEL);
    gtk_window_set_title(GTK_WINDOW(main_window), "ELEC3607 Lab 1");
    gtk_window_set_default_size(GTK_WINDOW(main_window), 400, 400);
    GtkWidget * drawing_area = gtk_drawing_area_new();

    /* Connect to the configure event to create the surface. */
    g_signal_connect(drawing_area, "configure-event", G_CALLBACK(drawing_area_configure_cb), NULL);

    gtk_container_add(GTK_CONTAINER(main_window), drawing_area);
    gtk_widget_show_all(main_window);

    /* Create a new thread to update the stored surface. */
    pthread_mutex_init( & mutex, NULL);
    pthread_create( & drawing_thread, NULL, thread_draw, NULL);

    gpio_init();

    /* create gpio threads */
    pthread_mutex_init( & mutexline, NULL);
    assert(pthread_create( & gpio_write_th, NULL, gpio_writer, NULL) == 0);

    /* Create a    timer to invalidate our window at 60Hz, and display the stored surface. */
    g_timeout_add(1000 / 60, invalidate_cb, drawing_area);

    /* Connect our redraw callback. */
    g_signal_connect(drawing_area, "draw", G_CALLBACK(drawing_area_draw_cb), NULL);

    /* Connect the destroy signal. */
    g_signal_connect(main_window, "destroy", G_CALLBACK(gtk_main_quit), NULL);

    gtk_main();

    /* block until thread 0 completes */
    pthread_join(gpio_write_th, NULL);
    fflush(stdout);

}

static gboolean
invalidate_cb(void * ptr) {
    if (GTK_IS_WIDGET(ptr)) {
        gtk_widget_queue_draw(GTK_WIDGET(ptr));
        return TRUE;
    }

    return FALSE;
}

static gboolean
drawing_area_configure_cb(GtkWidget * widget, GdkEventConfigure * event) {
    if (event -> type == GDK_CONFIGURE) {
        pthread_mutex_lock( & mutex);

        if (surface != (cairo_surface_t * ) NULL) {
            cairo_surface_destroy(surface);
        }

        GtkAllocation allocation;
        gtk_widget_get_allocation(widget, & allocation);
        surface = cairo_image_surface_create(CAIRO_FORMAT_ARGB32, allocation.width, allocation.height);
        surface_width = allocation.width;
        surface_height = allocation.height;

        pthread_mutex_unlock( & mutex);
    }

    return TRUE;
}

static void
drawing_area_draw_cb(GtkWidget * widget, cairo_t * context, void * ptr) {
    /* Copy the contents of the surface to the current context. */
    pthread_mutex_lock( & mutex);

    if (surface != (cairo_surface_t * ) NULL) {
        cairo_set_source_surface(context, surface, 0, 0);
        cairo_paint(context);
    }

    pthread_mutex_unlock( & mutex);
}

static void *
    thread_draw(void * ptr) {
        int redraw_number = 0;

        while (1) {
            // usleep (1E6 / 60); /* Sleep for 60 Hz. */
            usleep(1E6 / 2); /* Sleep for 60 Hz. */

            if (surface == (cairo_surface_t * ) NULL) {
                continue;
            }

            pthread_mutex_lock( & mutex);

            cairo_t * context = cairo_create(surface);

            /* Draw the background. */
            cairo_set_source_rgb(context, 1, 1, 1);
            cairo_rectangle(context, 0, 0, surface_width, surface_height);
            cairo_fill(context);

            int ssd[7][4] = {
                {
                    50,
                    50,
                    50,
                    4
                },
                {
                    100,
                    50,
                    4,
                    50
                },
                {
                    100,
                    100,
                    4,
                    50
                },
                {
                    50,
                    150,
                    54,
                    4
                },
                {
                    50,
                    100,
                    4,
                    50
                },
                {
                    50,
                    50,
                    4,
                    50
                },
                {
                    50,
                    100,
                    50,
                    4
                }
            };
            cairo_set_source_rgb(context, 0.5, 0.5, 0);
            unsigned char state = gpio_state();
            for (int j = 0; j < LINES; j++) {
                if (state & (1 << j))
                    cairo_rectangle(context, ssd[j][0], ssd[j][1], ssd[j][2], ssd[j][3]);
            }
            cairo_fill(context);

            redraw_number++;
            cairo_destroy(context);

            pthread_mutex_unlock( & mutex);
        }

        return NULL;
    }

/* EOF */
