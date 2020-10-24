This directory contains the arduino code to log data from the TEROS-12 sensors. 

# Getting started

1. Install the Arduino IDE: https://www.arduino.cc/en/main/software
2. Plug the TEROS-12 cables into the Arduino. The orange wire is data (goes to pin 13), brown is power (goes to 5V) and the silver/unshielded cable is ground (GND). There are multiple GND pins on the Arduino baord, it doesn't matter which one you use. 

![Data wire](https://raw.githubusercontent.com/lab11/soil-battery/master/arduino/images/20201023_172526.jpg)
![Power and GND](https://raw.githubusercontent.com/lab11/soil-battery/master/arduino/images/20201023_172538.jpg)

3. Open SDISerial/SDISerial.ino in the Arduino IDE
4. Plug the Arduino into your laptop to program it. Go to the Tools menu in the Arduino IDE and make sure that the correct Board and Port are set.
5. Build and upload the code to the Arduino by pressing the -> button on the top left of the IDE window. When programming is done, the final output in the bottom of the window will say "avrdude done.  Thank you."
6. Check that the sensor readings look correct by viewing the Serial Monitor (Tools->Serial Monitor). The baud rate needs to be set to 1200. Wait a few seconds, and you should start seeing data appear. The data should look like this:

0+1823.42+22.2+0

This corresponds to (sensor_id+raw_soil_moisture+temp+electrical_conductivity).

Congrats, you've successfully programmed the Arduino to read data from the TEROS-12 sensor!

# Preparing the Arduino for long-term deployment
Using the SDI-12 protocol, each Arduino can collect data from multiple sensors. To use this cabability, twist together the wires ends and plug them in as directed above. The wires can pull out of the Arduino pin holes rather easily, so I recommend putting the Arduino in a plastic case and puting the TEROS wires through the square hole opposite the USB port. Then you can secure the cable into place using hot glue or some similar material. Finally, tape the case together so it doesn't fall apart. These measures have worked for the Stanford TEROS setup, which has been carted all over the place and hasn't required any repairs/adjustment for more than a year.

![tape and glue](https://raw.githubusercontent.com/lab11/soil-battery/master/arduino/images/20201023_172453.jpg)
![sensor ready](https://raw.githubusercontent.com/lab11/soil-battery/master/arduino/images/20201023_172437.jpg)


Finally, plug the Arduino into a Shepherd or Rocketlogger. Shepherds/Rocketloggers contain an SD card, which is where the sensor data will be recorded.

# Additional info 

The `TEROS_Integrator_Guide.pdf` documents the serial protocol(s) the loggers use. We use the SDI-12 serial variant. 
