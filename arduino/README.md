This directory contains the arduino code to log data from the TEROS-12 sensors. 

# Getting started

1. Install the Arduino IDE: https://www.arduino.cc/en/main/software
2. Plug the TEROS-12 cables into the Arduino. The orange wire is data (goes to pin 13), brown is power (goes to 5V) and the silver/unshielded cable is ground (GND). There are multiple GND pins on the Arduino baord, it doesn't matter which one you use. 
3. Open SDISerial/SDISerial.ino in the Arduino IDE
4. Plug the Arduino into your laptop to program it. Go to the Tools menu in the Arduino IDE and make sure that the correct Board and Port are set.
5. Build and upload the code to the Arduino by pressing the -> button on the top left of the IDE window. When programming is done, the final output in the bottom of the window will say "avrdude done.  Thank you."
6. Check that the sensor readings look correct by viewing the Serial Monitor (Tools->Serial Monitor). The baud rate needs to be set to 1200. Wait a few seconds, and you should start seeing data appear. It should look like this:

0+1823.42+22.2+0

Congrats, you've successfully programmed the Arduino to read data from the TEROS-12 sensor!

# Preparing the Arduino for long-term deployment
TODO

# Additional info 

The `TEROS_Integrator_Guide.pdf` documents the serial protocol(s) the loggers use. We use the SDI-12 serial variant. 
