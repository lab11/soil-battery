#include <stdlib.h>
#include <stdint.h>
#include <ctype.h>
#include <stdio.h>   /* Standard input/output definitions */
#include <string.h>  /* String function definitions */
#include <unistd.h>  /* UNIX standard function definitions */
#include <fcntl.h>   /* File control definitions */
#include <errno.h>   /* Error number definitions */
#include <termios.h> /* POSIX terminal control definitions */
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>

uint8_t inbuf[1];
uint8_t outbuf[50];
char *logpath = "logs"; //"/home/rocketlogger/soil_battery";
char *pidpath = "logs/spitter.pid"; //"/run/teroslogger.pid";

// TODOs:
//  - better format checking before fwrite (some lines in logfile end up f'd up occasionally)
// PS: I have no idea what I'm doing!

int main(int argc, char** argv){
    /* cli args parse */
    int help = 0;
    char *tty_path = NULL;
    int index;
    int c;
    opterr = 0;
    while ((c = getopt (argc, argv, "t:")) != -1) {
        switch (c) {
            case 't':
                tty_path = optarg;
                break;
            case '?':
                if (optopt == 't')
                    fprintf (stderr, "Option -%c requires an argument.\n", optopt);
                else if (isprint(optopt))
                    fprintf (stderr, "Unknown option `-%c'.\n", optopt);
                else
                    fprintf (stderr, "Unknown option character `\\x%x'.\n", optopt);
                exit(1);
            default:
                abort();
        }
    }

    if (help) {
        printf("usage: %s [-lh] [-t tty]\n", argv[0]);
        printf("-t tty\t: set path to tty device file\n");
        exit(0);
    }

    //unmask the file mode for shits and giggles
    umask(0);

    int USB;
    if (tty_path) {
        USB = open( tty_path, O_WRONLY|O_NOCTTY|O_NONBLOCK );
    }
    else {
        USB = open( "/dev/ttys1", O_WRONLY|O_NOCTTY|O_NONBLOCK ); // "/dev/ttyACM0"
    }
    printf("USB = %d\n", USB);

    if (USB == -1) {
        printf("serial port open bad :( \n");
        exit(1);
    }
    else{
        printf("serial port open good\n");
    }

    struct termios tty;
    memset (&tty, 0, sizeof tty);

    if (tcgetattr(USB, &tty) != 0) {
        printf("Error fetching tty config, %i\n",errno);
    }
    /* Set Baud Rate */
    cfsetospeed (&tty, (speed_t)B1200);
    cfsetispeed (&tty, (speed_t)B1200);

    tty.c_cflag = (tty.c_cflag & ~CSIZE) | CS8;     // 8-bit chars
    tty.c_iflag &= ~IGNBRK;         // disable break processing
    tty.c_lflag = 0;                // no signaling chars, no echo,
    // no canonical processing
    tty.c_oflag = 0;                // no remapping, no delays
    tty.c_cc[VMIN]  = 0;            // read doesn't block
    tty.c_cc[VTIME] = 100;            // 10 seconds read timeout

    tty.c_iflag &= ~(IXON | IXOFF | IXANY); // shut off xon/xoff ctrl

    tty.c_cflag |= (CLOCAL | CREAD);// ignore modem controls,
    // enable reading
    tty.c_cflag &= ~(PARENB | PARODD);      // shut off parity
    tty.c_cflag &= ~CSTOPB;                 // use only one stop bit
    tty.c_cflag &= ~CRTSCTS;                // ?? not in POSIX... is this necessary?


    /* Flush Port, then applies attributes */
    tcflush( USB, TCIFLUSH );
    if (tcsetattr(USB, TCSANOW, &tty) != 0) {
        printf("Error configuring tty, %i\n", errno);
    }

	while(1) {
		printf("type a string to send: ");
		scanf("%s", &outbuf);
		write(USB, outbuf, sizeof outbuf);
		printf("wrote '%s' to the port\n", outbuf);
		sleep(3);
	}
}
