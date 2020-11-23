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
char *pidpath = "logs/stream.pid"; //"/run/teroslogger.pid";

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
        USB = open( tty_path, O_RDONLY|O_NOCTTY|O_NONBLOCK );
    }
    else {
        USB = open( "/dev/ttys1", O_RDONLY|O_NOCTTY|O_NONBLOCK ); // "/dev/ttyACM0"
    }
    printf("USB = %d\n", USB);

    if (USB == -1) {
        printf("serial port open bad :( \n");
        exit(1);
    }
    else{
        printf("serial port open good\n");
    }

    if (fcntl(USB, F_SETFL, 0) == -1) // apparently this is necessary
    {
        printf("can't set tty device non-blocking\n");
        exit(1);
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

    FILE* outfile;
    FILE* pidfile;
    char filename[100];
    pid_t process_id = 0;
    pid_t sid = 0;

    /* keep reading until start of line */
    //do {
    //    read(USB, inbuf, sizeof inbuf);
    //} while (inbuf[0] != '\n');
    
    printf("Synced\n");
    sprintf(filename, "%s/TEROSoutput-%lu.csv", logpath, (unsigned long) time(NULL));
    
    /* ignore the fork for now
    // Create child process so we can kill the parent and do setsid() on the child
    // in order to free the controlling terminal
    process_id = fork();
    // Indication of fork() failure
    if (process_id < 0) {
        printf("fork failed!\n");
        // Return failure in exit status
        exit(1);
    }

    // PARENT PROCESS. Need to kill it. 
    if (process_id > 0) {
        // write PID to pid file so we can kill logging later
        pidfile = fopen(pidpath, "wb");
        printf("process_id of child process %d\n", process_id);
        fprintf(pidfile, "%d", process_id);
        fflush(pidfile);
        fclose(pidfile);
        // return success in exit status
        exit(0);
    }

    //set new session. this makes the child independent from the controlling terminal
    sid = setsid();
    if (sid < 0) {
        // Return failure
        exit(1);
    }

    close(STDIN_FILENO);  // ?? why do we do this? does it improve performance? 
    close(STDOUT_FILENO);
    close(STDERR_FILENO);
    */

    outfile = fopen(filename, "wb");
    //TEROS-12 OUTPUT FORMAT: samples(ADDR/RAW/TMP/EC): 0+1870.34+21.1+0
    char header[] = "timestamp,sensorID,raw_VWC,temp,EC\n";
    fwrite(header, sizeof(char), sizeof(header), outfile); // write CSV header
    fflush(outfile);

    //printf("writing first\n");
    //fflush(stdout);
    //write(USB, "first\n", 6);
    //printf("done writing\n");
    //sleep(5);
    //printf("done sleeping\n");
    //fflush(stdout);

    // finally start reading and logging measurements
    int marker_state = 0;
    char logstr[80];
    // clear the logstr to get rid of garbage
    memset(logstr, 0, sizeof(logstr));
    // start reading and logging bytes forever
    while (1) {
        read(USB, inbuf, sizeof inbuf); // read in a byte
        printf("read character '%c'", inbuf[0]);
        fflush(stdout);
        if (inbuf[0] == '\n') { // if we reached the end of a measurement
            if (marker_state > 0) {
                // if this wasn't an empty line, toss a null terminator to the output string,
                // slap a time stamp on our measurement, and write that bad boi to file
                outbuf[marker_state] = 0; // this should let us avoid having to memset outbuf every time
                sprintf(logstr, "%lu,%s\n", (unsigned long) time(NULL), outbuf);
                fwrite(logstr, sizeof(char), sizeof(logstr), outfile); 
                fflush(outfile);
                
                // then reset our writing index and wait a sec before reading again
                marker_state = 0;
                sleep(1);
                //write(USB, "help\n", 5);
                //sleep(5);
            }
        } else if (marker_state >= sizeof outbuf){ //oops, overflow
            // just skip this trash if it overflows, so eat bytes until we reach the next newline
            do {
                read(USB, inbuf, sizeof inbuf);
            } while (inbuf[0] != '\n');
            // reset the marker to the beginning
            marker_state = 0;
        } else {
            // we write the new byte into our outbuf, replacing '+' with ',' for csv,
            // and increment the writing index
            if (inbuf[0] == '+') {
                outbuf[marker_state] = ',';
            } else {
                outbuf[marker_state] = inbuf[0];
            }
            marker_state += 1;
        }
    }
    
    // this doesn't ever run, but for the sake of completion -- for the sole purpose of soothing
    // our souls -- we will include the following two lines
    fclose(outfile);
    return 0;
}
