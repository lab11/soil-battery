#include <stdio.h>
#include <fcntl.h>   /* File Control Definitions           */
#include <termios.h> /* POSIX Terminal Control Definitions */
#include <unistd.h>  /* UNIX Standard Definitions      */ 
#include <errno.h>   /* ERROR Number Definitions           */

int main(void)
    {
  int fd;           //device file id
//------------------------------- Opening the Serial Port -------------------------------
    fd = open("/dev/tty.Bluetooth-Incoming-Port",O_RDWR | O_NOCTTY);    // ttyUSB0 is the FT232 based USB2SERIAL Converter 
    if(fd == -1)                        // Error Checking 
    printf("Error while opening the device\n");
//---------- Setting the Attributes of the serial port using termios structure ---------
    struct termios SerialPortSettings;  // Create the structure                          
    tcgetattr(fd, &SerialPortSettings); // Get the current attributes of the Serial port
// Setting the Baud rate
  cfsetispeed(&SerialPortSettings,B19200); // Set Read  Speed as 19200                       
    cfsetospeed(&SerialPortSettings,B19200); // Set Write Speed as 19200                       

    SerialPortSettings.c_cflag &= ~PARENB;   // Disables the Parity Enable bit(PARENB),So No Parity   
    SerialPortSettings.c_cflag &= ~CSTOPB;   // CSTOPB = 2 Stop bits,here it is cleared so 1 Stop bit 
    SerialPortSettings.c_cflag &= ~CSIZE;    // Clears the mask for setting the data size             
    SerialPortSettings.c_cflag |=  CS8;      // Set the data bits = 8                                 
    SerialPortSettings.c_cflag &= ~CRTSCTS;       // No Hardware flow Control                         
    SerialPortSettings.c_cflag |= CREAD | CLOCAL; // Enable receiver,Ignore Modem Control lines        
    SerialPortSettings.c_iflag &= ~(IXON | IXOFF | IXANY);  // Disable XON/XOFF flow control both i/p and o/p 
    SerialPortSettings.c_iflag &= ~(ICANON | ECHO | ECHOE | ISIG);  // Non Cannonical mode 
    SerialPortSettings.c_oflag &= ~OPOST;//No Output Processing
// Setting Time outs 
    SerialPortSettings.c_cc[VMIN] = 13; // Read at least 10 characters 
    SerialPortSettings.c_cc[VTIME] = 0; // Wait indefinetly  

    if((tcsetattr(fd,TCSANOW,&SerialPortSettings)) != 0) // Set the attributes to the termios structure
    printf("Error while setting attributes \n");
    //------------------------------- Read data from serial port -----------------------------

    char read_buffer[32];   // Buffer to store the data received              
    int  bytes_read = 0;    // Number of bytes read by the read() system call 
  int bytes_written = 0;  // Number of bytes written
    int i = 0;

    tcflush(fd, TCIFLUSH);   // Discards old data in the rx buffer            
//Device intialization

  char write_buffer[]="READ? \n ";
  bytes_written=write(fd,&write_buffer,sizeof(write_buffer));

  //sleep(2);

  bytes_read = read(fd,&read_buffer,32); // Read the data                   

    for(i=0;i<13;i++)    //printing only the needed characters
    printf("%c",read_buffer[i]);
    close(fd); // Close the serial port

    }