//[12f23eddde] 20-01-23 a better timer
//[12f23eddde] 20-01-23 add time offset

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <fcntl.h>
#include <sys/ioctl.h>
//#include <linux/input.h> // this does not compile
#include <unistd.h>
#include <errno.h>
#include <sys/time.h>  // Modified

// from <linux/input.h>

typedef uint32_t        __u32;
typedef uint16_t        __u16;
typedef __signed__ int  __s32;

struct input_event {
    struct timeval time;
    __u16 type;
    __u16 code;
    __u32 value;
};

#define MICROSEC 1000000
#define TRUNC(x) ( x > 0 ? x : 0 ) // avoid uint overflow

#define EVIOCGVERSION		_IOR('E', 0x01, int)			/* get driver version */
#define EVIOCGID		_IOR('E', 0x02, struct input_id)	/* get device ID */
#define EVIOCGKEYCODE		_IOR('E', 0x04, int[2])			/* get keycode */
#define EVIOCSKEYCODE		_IOW('E', 0x04, int[2])			/* set keycode */

#define EVIOCGNAME(len)		_IOC(_IOC_READ, 'E', 0x06, len)		/* get device name */
#define EVIOCGPHYS(len)		_IOC(_IOC_READ, 'E', 0x07, len)		/* get physical location */
#define EVIOCGUNIQ(len)		_IOC(_IOC_READ, 'E', 0x08, len)		/* get unique identifier */

#define EVIOCGKEY(len)		_IOC(_IOC_READ, 'E', 0x18, len)		/* get global keystate */
#define EVIOCGLED(len)		_IOC(_IOC_READ, 'E', 0x19, len)		/* get all LEDs */
#define EVIOCGSND(len)		_IOC(_IOC_READ, 'E', 0x1a, len)		/* get all sounds status */
#define EVIOCGSW(len)		_IOC(_IOC_READ, 'E', 0x1b, len)		/* get all switch states */

#define EVIOCGBIT(ev,len)	_IOC(_IOC_READ, 'E', 0x20 + ev, len)	/* get event bits */
#define EVIOCGABS(abs)		_IOR('E', 0x40 + abs, struct input_absinfo)		/* get abs value/limits */
#define EVIOCSABS(abs)		_IOW('E', 0xc0 + abs, struct input_absinfo)		/* set abs value/limits */

#define EVIOCSFF		_IOC(_IOC_WRITE, 'E', 0x80, sizeof(struct ff_effect))	/* send a force effect to a force feedback device */
#define EVIOCRMFF		_IOW('E', 0x81, int)			/* Erase a force effect */
#define EVIOCGEFFECTS		_IOR('E', 0x84, int)			/* Report number of effects playable at the same time */

#define EVIOCGRAB		_IOW('E', 0x90, int)			/* Grab/Release device */

// end <linux/input.h>

long long get_usec(struct timeval *tv_ptr){
    gettimeofday(tv_ptr, NULL);
    return 1000000 * tv_ptr->tv_sec + tv_ptr->tv_usec;
}

void remove_specific_chars(char* str, char c1, char c2) {
    char *pr = str, *pw = str;
    while (*pr) {
        *pw = *pr++;
        pw += (*pw != c1 && *pw != c2);
    }
    *pw = '\0';
}

int main(int argc, char *argv[])
{
    int fd;
    int ret;
    int version;
    struct input_event event;
    struct timeval tv;
    long offset = 0;
    int act_cnt = 0;

    if(argc != 3 && argc != 4) {
        fprintf(stderr, "usage: %s input_device input_events offset\n", argv[0]);
        return 1;
    }

    fd = open(argv[1], O_RDWR);
    if(fd < 0) {
        fprintf(stderr, "could not open %s, %s\n", argv[optind], strerror(errno));
        return 1;
    }
    if (ioctl(fd, EVIOCGVERSION, &version)) {
        fprintf(stderr, "could not get driver version for %s, %s\n", argv[optind], strerror(errno));
        return 1;
    }

    FILE * fd_in = fopen(argv[2], "r");
    if (fd_in == NULL) {
        fprintf(stderr, "could not open input file: %s\n", argv[2]);
        return 1;
    }

    if (strlen(argv[3])!=0) offset = strtol(argv[3], NULL, 10);
    printf("[mysendevent] trace=%s offset=%ld(ms)\n",argv[1],offset);

    char line[128];
    unsigned int sleep_time;
    double timestamp_init = -1.0;
    double timestamp_now;
    long long usec_init = -1;
    char type[32];
    char code[32];
    char value[32];

    // future
    // read(fd, &event, sizeof(event));
    // printf("Got input from %s\n",argv[1]);

    while (fgets(line, sizeof(line), fd_in) != NULL) {
        // remove the characters [ and ] surrounding the timestamp
        remove_specific_chars(line, '[', ']');
        sscanf(line, "%lf %s %s %s", &timestamp_now, type, code, value);

        // write the event to the appropriate input device
        memset(&event, 0, sizeof(event));
        event.type = (int) strtol(type, NULL, 16);
        event.code = (int) strtol(code, NULL, 16);
        event.value = (uint32_t) strtoll(value, NULL, 16);

        if(timestamp_init != -1.0)
        {
            // In order to playback the same gestures the code sleeps accordingly to the timestamps from the inputed recording
            long long usec_now = get_usec(&tv);
            long long sleep_time_fixed = (long long)((timestamp_now - timestamp_init) * MICROSEC) - (usec_now - usec_init) + offset*1000;
            sleep_time = TRUNC(sleep_time_fixed);  // more accurate
            if(sleep_time!=0){
                printf("[%4d] sleep_time = (%lf-%lf)*1000000 - (%lld - %lld) + %ld*1000 = %u (us)\n",
                        act_cnt,timestamp_now,timestamp_init,usec_now,usec_init, offset, sleep_time);
                act_cnt++;  // update val
            }
            // we don't care about the value of a single event's timestamp but the difference between two sequential events
            usleep(sleep_time); // sleep_time is in MICROSECONDS
        }

        // write event
        ret = write(fd, &event, sizeof(event));
        if(ret < sizeof(event)) {
            fprintf(stderr, "write event failed, %s\n", strerror(errno));
            return -1;
        }

        // set init val
        if(usec_init == -1){
            usec_init = get_usec(&tv);
        }
        if(timestamp_init == -1.0){
            timestamp_init = timestamp_now;
        }

        // Clear temporary buffers
        memset(line, 0, sizeof(line));
        memset(type, 0, sizeof(type));
        memset(code, 0, sizeof(code));
        memset(value, 0, sizeof(value));
    }

    fclose(fd_in);
    close(fd);

    return 0;
}