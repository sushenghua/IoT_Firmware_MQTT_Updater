# IoT_Firmware_MQTT_Updater

**steps to run**

1. clone the code
```
git clone git@github.com:sushenghua/IoT_Firmware_MQTT_Updater.git
```

2. setup config.py
set WORKING_PATH to the full path of folder containing this file
```
WORKING_PATH                               = 'fullPahtOfThisDirectory'
```

3. prepare CA files (follow [Certificates in mosquitto](http://www.steves-internet-guide.com/creating-and-using-client-certificates-with-mqtt-and-mosquitto/) to learn how to generate
CA files and configurate them in the mosquitto broker. A handy script to generate CA files can be found at [here](https://github.com/sushenghua/IoT_Firmware_MQTT_Updater/blob/master/ca/genCA.sh))
and copy 'ca.crt' into 'ca' foler.

4. prepare firmware bin file. For example, if the new binary named SensorApp.bin, version 1.10, board version 1.36, run the following script will generate description
file for this binary to be used in 'firmware_updater.py'
```
python gen_description.py -v 1.10 -r 1.36 -b SensorApp.bin
```

5. run the program
```
python firmware_updater.py
```
